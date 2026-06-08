from draw import foguete, planeta, abertura
from models import Body, Mission, Route, MissionProfile
from data_structures import Stack, Queue
from algorithms import linear_search, binary_search, bubble_sort
from graph import build_graph, find_best_route, km_s_to_mkm_per_day, choose_profile, MISSION_PROFILES
from visualizer import plot_route, plot_mission_comparison
from api_loader import load_bodies


API_KEY = "fff526c8-f44b-4f45-93ce-2f48c97ed35a"

ROCKET_PROFILES = {
    "1": ("Falcon 9",  7.9),
    "2": ("Saturn V",  11.2),
    "3": ("Ariane 5",  7.8),
    "4": ("SLS",       10.8),
}

def print_body(body: Body) -> None:
    print(
        f"  - {body.name:<10} | {body.body_type:<8} "
        f"| {body.distance_mkm:>8.2f} Mkm "
        f"| gravidade {body.gravity} m/s²"
    )


def route_to_text(route: Route) -> str:
    return " → ".join(b.name for b in route.path)


def print_route(route: Route) -> None:
    c = route.criteria
    print(f"\n  [ROTA]        {route_to_text(route)}")
    print(f"  [DISTANCIA]   {route.distance_mkm} Mkm")
    print(f"  [TEMPO]       {route.travel_time_days} dias")
    print(f"  [COMBUSTIVEL] {route.fuel_cost}")
    print(f"  [SCORE]       {route.score}")
    print(
        f"  [PERFIL]      {c.get('perfil')}  |  "
        f"dist={c.get('w_dist')}  tempo={c.get('w_tempo')}  "
        f"comb={c.get('w_comb')}  grav={c.get('w_grav')}  "
        f"prior={c.get('priority')}"
    )


def choose_rocket() -> tuple[str, float]:
    print(foguete)
    print("  Escolha um foguete:")
    for key, (name, speed_km_s) in ROCKET_PROFILES.items():
        print(f"    {key} - {name} ({speed_km_s} km/s)")
    choice = input("  Opcao: ").strip()
    rocket = ROCKET_PROFILES.get(choice)
    if rocket is None:
        raise ValueError("foguete invalido")
    name, speed_km_s = rocket
    return name, km_s_to_mkm_per_day(speed_km_s)




def main() -> None:
    print(abertura)

    # Variáveis para lazy loading
    bodies: list[Body] | None = None
    sorted_bodies: list[Body] | None = None
    graph: dict[Body, list[GraphEdge]] | None = None

    def ensure_bodies_loaded() -> None:
        """Carrega os dados sob demanda na primeira requisição."""
        nonlocal bodies, sorted_bodies, graph
        if bodies is None:
            bodies = load_bodies(api_key=API_KEY)
            sorted_bodies = bubble_sort(bodies)
            graph = build_graph(bodies)
            print(f"[INFO] Dados carregados: {len(bodies)} corpos, {sum(len(v) for v in graph.values())} arestas")

    missions: Queue = Queue()
    history: Stack = Stack()

    rocket_name = "Falcon 9"
    rocket_speed = km_s_to_mkm_per_day(7.9)

    print("[INFO] Planejador de rota iniciado (dados sob demanda)")

    while True:
        print()
        print("  1 - Listar corpos (ordenados por distância)")
        print("  2 - Buscar corpo por nome  (busca linear)")
        print("  3 - Buscar corpo por distância (busca binária)")
        print("  4 - Calcular rota  (grafo multicritério)")
        print("  5 - Enfileirar missao")
        print("  6 - Processar fila de missoes")
        print("  7 - Desfazer ultima rota  (pilha)")
        print("  8 - Comparar missoes processadas (gráfico)")
        print("  9 - Escolher foguete")
        print("  0 - Sair")
        print(f"  [Foguete atual: {rocket_name}  |  Missoes na fila: {len(missions)}  |  Histórico: {len(history)}]")
        print("═" * 52)

        choice = input("  Opcao: ").strip()

        try:
            # ── 1. Listar corpos ──────────────────────────
            if choice == "1":
                ensure_bodies_loaded()
                print(planeta)
                for body in sorted_bodies:
                    print_body(body)

            # ── 2. Busca linear ───────────────────────────
            elif choice == "2":
                ensure_bodies_loaded()
                name = input("  Nome: ").strip()
                body = linear_search(bodies, name)
                if body is None:
                    print("[INFO] corpo nao encontrado")
                else:
                    print_body(body)

            # ── 3. Busca binária ──────────────────────────
            elif choice == "3":
                ensure_bodies_loaded()
                try:
                    dist = float(input("  Distância (Mkm): ").strip())
                except ValueError:
                    print("[ERRO] valor invalido")
                    continue
                body = binary_search(sorted_bodies, dist)
                if body is None:
                    print("[INFO] nenhum corpo com essa distância exata")
                    print("[INFO] corpos próximos:")
                    for b in sorted_bodies:
                        if abs(b.distance_mkm - dist) < 200:
                            print_body(b)
                else:
                    print_body(body)

            # ── 4. Calcular rota ──────────────────────────
            elif choice == "4":
                ensure_bodies_loaded()
                origin_name = input("  Origem: ").strip()
                dest_name   = input("  Destino: ").strip()

                origin = linear_search(bodies, origin_name)
                dest   = linear_search(bodies, dest_name)

                if origin is None or dest is None:
                    print("[ERRO] origem ou destino invalido")
                    continue
                if origin.name == dest.name:
                    print("[ERRO] origem e destino devem ser diferentes")
                    continue

                profile = choose_profile()
                try:
                    priority = int(input("  Prioridade (1=normal / 2=alta / 3=urgente): ").strip())
                    priority = max(1, min(3, priority))
                except ValueError:
                    priority = 1

                route = find_best_route(graph, origin, dest, rocket_speed, profile, priority)
                history.push(route)
                print_route(route)
                plot_route(route, bodies, filename="route_map.png")

            # ── 5. Enfileirar missão ──────────────────────
            elif choice == "5":
                ensure_bodies_loaded()
                origin_name = input("  Origem: ").strip()
                dest_name   = input("  Destino: ").strip()
                profile = choose_profile()
                try:
                    priority = int(input("  Prioridade (1=normal / 2=alta / 3=urgente): ").strip())
                    priority = max(1, min(3, priority))
                except ValueError:
                    priority = 1
                missions.enqueue(Mission(origin_name, dest_name, priority, profile))
                print(f"[INFO] missao enfileirada com perfil '{profile.name}'  (fila: {len(missions)} missoes)")

            # ── 6. Processar fila ─────────────────────────
            elif choice == "6":
                ensure_bodies_loaded()
                if missions.empty():
                    print("[INFO] fila vazia")
                    continue
                processed: list[Route] = []
                while not missions.empty():
                    mission = missions.dequeue()
                    origin  = linear_search(bodies, mission.origin)
                    dest    = linear_search(bodies, mission.destination)
                    if origin is None or dest is None:
                        print(f"[ERRO] missao invalida: {mission.origin} -> {mission.destination}")
                        continue
                    route = find_best_route(graph, origin, dest, rocket_speed, mission.profile, mission.priority)
                    history.push(route)
                    processed.append(route)
                    print(f"[INFO] processando {mission.origin} -> {mission.destination}")
                    print_route(route)

                if processed:
                    plot_mission_comparison(processed, filename="mission_comparison.png")

            # ── 7. Desfazer última rota ───────────────────
            elif choice == "7":
                if history.empty():
                    print("[INFO] nada para desfazer")
                else:
                    route = history.pop()
                    print(f"[INFO] rota removida do historico: {route_to_text(route)}")
                    print(f"[INFO] historico restante: {len(history)} rotas")

            # ── 8. Comparar missões ───────────────────────
            elif choice == "8":
                all_routes: list[Route] = []
                temp: Stack = Stack()
                while not history.empty():
                    r = history.pop()
                    all_routes.append(r)
                    temp.push(r)
                while not temp.empty():
                    history.push(temp.pop())

                if not all_routes:
                    print("[INFO] nenhuma rota no historico")
                else:
                    plot_mission_comparison(all_routes[:8], filename="mission_comparison.png")

            # ── 9. Escolher foguete ───────────────────────
            elif choice == "9":
                rocket_name, rocket_speed = choose_rocket()
                print(f"[INFO] foguete selecionado: {rocket_name}")
                print(f"[INFO] velocidade: {rocket_speed:.4f} Mkm/dia")

            elif choice == "0":
                print("[INFO] encerrando o planejador")
                break

            else:
                print("[AVISO] opcao invalida")

        except (IndexError, ValueError) as exc:
            print(f"[ERRO] {exc}")


if __name__ == "__main__":
    main()