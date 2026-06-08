"""
Módulo: graph.py
Grafo de rotas espaciais com critérios múltiplos:
  - Distância (Mkm)
  - Tempo de viagem (dias)
  - Custo de combustível estimado
  - Penalidade de gravidade do destino
  - Prioridade da missão

Os pesos de cada critério são definidos pelo PERFIL DA MISSÃO,
escolhido pelo usuário em tempo de execução.
"""

from __future__ import annotations
from dataclasses import dataclass
from models import Body, GraphEdge, Route, MissionProfile
from data_structures import LinkedList


# ──────────────────────────────────────────────
# Perfis de missão (pesos dinâmicos)
# ──────────────────────────────────────────────


MISSION_PROFILES: dict[str, MissionProfile] = {
    "1": MissionProfile(
        name="Econômica",
        description="Minimiza combustível — ideal para carga não urgente",
        w_distance=0.15,
        w_time=0.10,
        w_fuel=0.60,
        w_gravity=0.15,
    ),
    "2": MissionProfile(
        name="Rápida",
        description="Minimiza tempo — ideal para missões de resgate",
        w_distance=0.20,
        w_time=0.60,
        w_fuel=0.10,
        w_gravity=0.10,
    ),
    "3": MissionProfile(
        name="Segura",
        description="Evita alta gravidade — ideal para pouso de precisão",
        w_distance=0.15,
        w_time=0.15,
        w_fuel=0.20,
        w_gravity=0.50,
    ),
    "4": MissionProfile(
        name="Balanceada",
        description="Pesos iguais entre todos os critérios",
        w_distance=0.25,
        w_time=0.25,
        w_fuel=0.25,
        w_gravity=0.25,
    ),
    "5": MissionProfile(
        name="Personalizada",
        description="Você define os pesos manualmente",
        w_distance=0.0,  # preenchido pelo usuário
        w_time=0.0,
        w_fuel=0.0,
        w_gravity=0.0,
    ),
}


def choose_profile() -> MissionProfile:
    """Exibe os perfis disponíveis e retorna o escolhido pelo usuário."""
    print("\n  Perfil da missão:")
    for key, p in MISSION_PROFILES.items():
        print(f"    {key} - {p.name:<14}  {p.description}")

    choice = input("  Perfil: ").strip()

    if choice not in MISSION_PROFILES:
        print("  [AVISO] perfil invalido, usando Balanceada")
        return MISSION_PROFILES["4"]

    profile = MISSION_PROFILES[choice]

    # Perfil personalizado: usuário digita os pesos
    if choice == "5":
        profile = _custom_profile()

    # Mostra resumo dos pesos ativos
    print(
        f"  [PERFIL] {profile.name} | "
        f"dist={profile.w_distance}  tempo={profile.w_time}  "
        f"comb={profile.w_fuel}  grav={profile.w_gravity}"
    )
    return profile


def _custom_profile() -> MissionProfile:
    """Lê os pesos do usuário e normaliza para soma = 1."""
    print("  Digite os pesos (serão normalizados automaticamente para soma = 1):")
    weights = {}
    for label in ("distancia", "tempo", "combustivel", "gravidade"):
        while True:
            try:
                val = float(input(f"    Peso {label}: ").strip())
                if val < 0:
                    raise ValueError
                weights[label] = val
                break
            except ValueError:
                print("    [ERRO] digite um número >= 0")

    total = sum(weights.values())
    if total == 0:
        print("  [AVISO] todos zeros, usando Balanceada")
        return MISSION_PROFILES["4"]

    return MissionProfile(
        name="Personalizada",
        description="Pesos definidos pelo usuário",
        w_distance=round(weights["distancia"] / total, 4),
        w_time=round(weights["tempo"] / total, 4),
        w_fuel=round(weights["combustivel"] / total, 4),
        w_gravity=round(weights["gravidade"] / total, 4),
    )


# ──────────────────────────────────────────────
# Grafo e cálculo de rota
# ──────────────────────────────────────────────

def km_s_to_mkm_per_day(speed_km_s: float) -> float:
    return speed_km_s * 86400 / 1_000_000


def _fuel_cost(distance_mkm: float, gravity_dest: float) -> float:
    """Custo de combustível: proporcional à distância e gravidade do destino."""
    return round(distance_mkm * 0.1 + gravity_dest * 5.0, 2)


def build_graph(bodies: list[Body]) -> dict[Body, list[GraphEdge]]:
    """Constrói grafo completo — todos os corpos conectados entre si."""
    graph: dict[Body, list[GraphEdge]] = {}
    for origin in bodies:
        edges: list[GraphEdge] = []
        for dest in bodies:
            if dest.name == origin.name:
                continue
            dist = abs(dest.distance_mkm - origin.distance_mkm)
            edges.append(
                GraphEdge(
                    destination=dest,
                    distance_mkm=round(dist, 2),
                    travel_time_days=0.0,      # calculado na busca com velocidade real
                    fuel_cost=_fuel_cost(dist, dest.gravity),
                    gravity_penalty=dest.gravity,
                )
            )
        graph[origin] = edges
    return graph


def _compute_score(
    total_dist: float,
    total_fuel: float,
    gravity_dest: float,
    speed_mkm_per_day: float,
    profile: MissionProfile,
    priority: int,
) -> float:
    """Score composto usando os pesos do perfil. Menor = melhor rota."""
    time = total_dist / speed_mkm_per_day
    raw = (
        profile.w_distance * total_dist
        + profile.w_time    * time
        + profile.w_fuel    * total_fuel
        + profile.w_gravity * gravity_dest
    )
    return round(raw / priority, 4)


def find_best_route(
    graph: dict[Body, list[GraphEdge]],
    origin: Body,
    destination: Body,
    speed_mkm_per_day: float,
    profile: MissionProfile,
    priority: int = 1,
) -> Route:
    """
    Encontra a melhor rota origem → destino usando os pesos do perfil.
    Avalia rota direta + todas as rotas com 1 escala intermediária.
    """

    def edge_for(src: Body, dst: Body) -> GraphEdge | None:
        for e in graph.get(src, []):
            if e.destination.name == dst.name:
                return e
        return None

    def make_route(path_bodies: list[Body], total_dist: float, total_fuel: float) -> Route:
        ll = LinkedList()
        for b in path_bodies:
            ll.append(b)
        time = total_dist / speed_mkm_per_day
        sc = _compute_score(
            total_dist, total_fuel,
            path_bodies[-1].gravity,
            speed_mkm_per_day, profile, priority,
        )
        return Route(
            path=ll,
            distance_mkm=round(total_dist, 2),
            travel_time_days=round(time, 2),
            fuel_cost=round(total_fuel, 2),
            score=sc,
            criteria={
                "perfil":   profile.name,
                "w_dist":   profile.w_distance,
                "w_tempo":  profile.w_time,
                "w_comb":   profile.w_fuel,
                "w_grav":   profile.w_gravity,
                "priority": priority,
            },
        )

    # ── Rota direta ──────────────────────────────
    direct = edge_for(origin, destination)
    if direct is None:
        raise ValueError(f"Aresta não encontrada: {origin.name} -> {destination.name}")

    best_route = make_route([origin, destination], direct.distance_mkm, direct.fuel_cost)

    # ── Rotas com 1 escala intermediária ─────────
    for mid_body in graph:
        if mid_body.name in {origin.name, destination.name}:
            continue
        leg1 = edge_for(origin, mid_body)
        leg2 = edge_for(mid_body, destination)
        if leg1 is None or leg2 is None:
            continue
        total_dist = leg1.distance_mkm + leg2.distance_mkm
        total_fuel = leg1.fuel_cost + leg2.fuel_cost
        candidate = make_route([origin, mid_body, destination], total_dist, total_fuel)
        if candidate.score < best_route.score:
            best_route = candidate

    return best_route