"""
Módulo: loader.py
Busca dados reais dos planetas na Solar System OpenData API.
https://api.le-systeme-solaire.net

Campos usados da API:
  englishName   → nome em inglês (mapeamos para pt-BR)
  gravity       → gravidade em m/s²
  semimajorAxis → eixo semi-maior em km (convertemos para Mkm)
  bodyType      → tipo do corpo ("Planet")

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

PLANET_IDS = ["mercure", "venus", "terre", "mars",
              "jupiter", "saturne", "uranus", "neptune"]




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

    if erros:
        raise RuntimeError(f"Erro ao carregar dados da API: {len(erros)} planeta(s) com falha")

    print(f"[API] {len(bodies)} corpos carregados com sucesso\n")
    return bodies


def load_bodies(api_key: str) -> list[Body]:
    return fetch_bodies(api_key)