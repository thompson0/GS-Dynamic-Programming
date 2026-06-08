"""
Módulo: loader.py
Busca dados reais dos planetas na Solar System OpenData API.
https://api.le-systeme-solaire.net

Campos usados da API:
  englishName   → nome em inglês (mapeamos para pt-BR)
  gravity       → gravidade em m/s²
  semimajorAxis → eixo semi-maior em km (convertemos para Mkm)
  bodyType      → tipo do corpo ("Planet")

Em caso de falha na API, usa dados locais como fallback.
"""

import requests
from models import Body

# ──────────────────────────────────────────────
# Configuração
# ──────────────────────────────────────────────

API_BASE = "https://api.le-systeme-solaire.net/rest"
TIMEOUT  = 8  # segundos

# Mapeamento inglês (API) → português (projeto)
NOME_PT: dict[str, str] = {
    "Mercury": "Mercurio",
    "Venus":   "Venus",
    "Earth":   "Terra",
    "Mars":    "Marte",
    "Jupiter": "Jupiter",
    "Saturn":  "Saturno",
    "Uranus":  "Urano",
    "Neptune": "Netuno",
}

# IDs dos planetas na API (em francês/minúsculo)
PLANET_IDS = ["mercure", "venus", "terre", "mars",
              "jupiter", "saturne", "uranus", "neptune"]

# Fallback local caso a API esteja fora ou a key seja inválida
FALLBACK_DATA: dict[str, dict] = {
    "Mercurio": {"body_type": "planet", "distance_mkm": 57.9,   "gravity": 3.7},
    "Venus":    {"body_type": "planet", "distance_mkm": 108.2,  "gravity": 8.87},
    "Terra":    {"body_type": "planet", "distance_mkm": 149.6,  "gravity": 9.81},
    "Marte":    {"body_type": "planet", "distance_mkm": 227.9,  "gravity": 3.71},
    "Jupiter":  {"body_type": "planet", "distance_mkm": 778.5,  "gravity": 24.79},
    "Saturno":  {"body_type": "planet", "distance_mkm": 1434.0, "gravity": 10.44},
    "Urano":    {"body_type": "planet", "distance_mkm": 2871.0, "gravity": 8.69},
    "Netuno":   {"body_type": "planet", "distance_mkm": 4495.1, "gravity": 11.15},
}


# ──────────────────────────────────────────────
# Funções de conversão
# ──────────────────────────────────────────────

def _km_to_mkm(km: float) -> float:
    """Converte km para milhões de km (Mkm)."""
    return round(km / 1_000_000, 2)


def _parse_body(data: dict) -> Body | None:
    """
    Converte o JSON da API em um objeto Body.
    Retorna None se faltar algum campo essencial.
    """
    try:
        nome_en  = data["englishName"]
        nome_pt  = NOME_PT.get(nome_en)
        if nome_pt is None:
            return None  # planeta não mapeado, ignora

        gravity      = float(data["gravity"])
        semi_axis_km = float(data["semimajorAxis"])
        distance_mkm = _km_to_mkm(semi_axis_km)
        body_type    = data.get("bodyType", "Planet").lower()

        return Body(
            name=nome_pt,
            body_type=body_type,
            distance_mkm=distance_mkm,
            gravity=round(gravity, 4),
        )
    except (KeyError, TypeError, ValueError):
        return None


# ──────────────────────────────────────────────
# Funções públicas
# ──────────────────────────────────────────────

def fetch_bodies(api_key: str) -> list[Body]:
    """
    Busca os 8 planetas na API e retorna lista de Body.
    Em caso de erro, usa os dados locais de fallback.

    Parâmetros:
        api_key: chave Bearer da Solar System OpenData API
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    bodies: list[Body] = []
    erros: list[str]   = []

    print("[API] Buscando dados dos planetas...")

    for planet_id in PLANET_IDS:
        url = f"{API_BASE}/bodies/{planet_id}"
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            body = _parse_body(resp.json())
            if body:
                bodies.append(body)
                print(f"  [OK] {body.name:<10} | dist: {body.distance_mkm} Mkm | grav: {body.gravity} m/s²")
            else:
                erros.append(planet_id)
        except requests.exceptions.Timeout:
            print(f"  [TIMEOUT] {planet_id} — timeout após {TIMEOUT}s")
            erros.append(planet_id)
        except requests.exceptions.HTTPError as e:
            print(f"  [ERRO HTTP] {planet_id} — {e}")
            erros.append(planet_id)
        except requests.exceptions.RequestException as e:
            print(f"  [ERRO REDE] {planet_id} — {e}")
            erros.append(planet_id)

    # Completa com fallback os planetas que falharam
    if erros:
        print(f"[API] {len(erros)} planeta(s) com falha — usando dados locais para: {', '.join(erros)}")
        nomes_ok = {b.name for b in bodies}
        for nome_pt, info in FALLBACK_DATA.items():
            if nome_pt not in nomes_ok:
                bodies.append(Body(
                    name=nome_pt,
                    body_type=info["body_type"],
                    distance_mkm=info["distance_mkm"],
                    gravity=info["gravity"],
                ))

    if not bodies:
        print("[API] Falha total — usando todos os dados locais")
        return _load_fallback()

    print(f"[API] {len(bodies)} corpos carregados com sucesso\n")
    return bodies


def _load_fallback() -> list[Body]:
    """Retorna lista de Body com os dados locais."""
    return [
        Body(name=n, body_type=i["body_type"],
             distance_mkm=i["distance_mkm"], gravity=i["gravity"])
        for n, i in FALLBACK_DATA.items()
    ]


def load_bodies(api_key: str | None = None) -> list[Body]:
    """
    Ponto de entrada principal.
    Se api_key for fornecida, busca da API.
    Caso contrário, usa dados locais diretamente.
    """
    if api_key:
        return fetch_bodies(api_key)
    print("[INFO] Sem API key — usando dados locais")
    return _load_fallback()