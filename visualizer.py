"""
Módulo: visualizer.py
Visualização das rotas com matplotlib:
  - Mapa orbital do sistema solar (eixo X = distância ao sol)
  - Rota destacada entre os corpos selecionados
  - Gráfico de comparação de scores de missões processadas
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from models import Body, Route


# Cores por corpo
BODY_COLORS = {
    "Mercurio": "#b5b5b5",
    "Venus":    "#e8cda0",
    "Terra":    "#4fa3e0",
    "Marte":    "#c1440e",
    "Jupiter":  "#c88b3a",
    "Saturno":  "#e4d191",
    "Urano":    "#7de8e8",
    "Netuno":   "#5b6ee1",
}

BODY_SIZES = {
    "Mercurio": 4,
    "Venus":    7,
    "Terra":    7,
    "Marte":    5,
    "Jupiter":  18,
    "Saturno":  15,
    "Urano":    11,
    "Netuno":   11,
}


def _log_dist(d: float) -> float:
    """Escala logarítmica para que os planetas internos fiquem visíveis."""
    return np.log10(d + 1)


def plot_route(route: Route, all_bodies: list[Body], filename: str = "route_map.png") -> str:
    """
    Gera mapa orbital mostrando todos os planetas e a rota escolhida.
    Salva em `filename` e retorna o caminho.
    """
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#0d0d1a")

    # Sol
    ax.scatter([0], [0], s=300, color="#FFD700", zorder=5, label="Sol")
    ax.text(0, 0.18, "Sol", ha="center", color="#FFD700", fontsize=8)

    # Todos os corpos
    for body in all_bodies:
        x = _log_dist(body.distance_mkm)
        color = BODY_COLORS.get(body.name, "#ffffff")
        size = BODY_SIZES.get(body.name, 6)
        ax.scatter([x], [0], s=size ** 2, color=color, zorder=4)
        ax.text(x, -0.22, body.name, ha="center", color=color, fontsize=7, rotation=45)

    # Rota destacada
    path_bodies: list[Body] = list(route.path)
    xs = [_log_dist(b.distance_mkm) for b in path_bodies]
    ys = [0] * len(xs)

    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        mid_x = (x0 + x1) / 2
        height = 0.4 if (i % 2 == 0) else -0.4
        ax.annotate(
            "",
            xy=(x1, 0),
            xytext=(x0, 0),
            arrowprops=dict(
                arrowstyle="->",
                color="#00ff99",
                lw=2,
                connectionstyle=f"arc3,rad={0.4 if height > 0 else -0.4}",
            ),
            zorder=6,
        )

    for i, body in enumerate(path_bodies):
        x = _log_dist(body.distance_mkm)
        label = "Origem" if i == 0 else ("Destino" if i == len(path_bodies) - 1 else "Escala")
        color = "#00ff99" if i == 0 else ("#ff4444" if i == len(path_bodies) - 1 else "#ffaa00")
        ax.scatter([x], [0], s=200, color=color, zorder=7, edgecolors="white", linewidths=1.5)
        ax.text(x, 0.28, label, ha="center", color=color, fontsize=8, fontweight="bold")

        info = (
        f"Rota: {' → '.join(b.name for b in path_bodies)}\n"
        f"Distância: {route.distance_mkm} Mkm  |  "
        f"Tempo: {route.travel_time_days} dias  |  "
        f"Combustível: {route.fuel_cost}  |  "
        f"Score: {route.score}"
    )
    ax.set_title(info, color="white", fontsize=9, pad=12)

    ax.set_xlim(-0.15, _log_dist(5000) + 0.1)
    ax.set_ylim(-0.6, 0.6)
    ax.axis("off")

    plt.tight_layout()
    plt.show()
    return filename


def plot_mission_comparison(routes: list[Route], filename: str = "mission_comparison.png") -> str:
    """
    Gráfico de barras comparando score, distância e tempo
    das últimas missões processadas.
    """
    if not routes:
        print("[VIS] nenhuma missao para comparar")
        return ""

    labels = [" → ".join(b.name for b in r.path) for r in routes]
    scores = [r.score for r in routes]
    distances = [r.distance_mkm for r in routes]
    times = [r.travel_time_days for r in routes]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 2.5), 5))
    fig.patch.set_facecolor("#0d0d1a")
    ax.set_facecolor("#0d0d1a")

    b1 = ax.bar(x - width, scores,    width, label="Score",          color="#00ff99", alpha=0.85)
    b2 = ax.bar(x,         distances,  width, label="Distância (Mkm)", color="#4fa3e0", alpha=0.85)
    b3 = ax.bar(x + width, times,     width, label="Tempo (dias)",    color="#ffaa00", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color="white", rotation=15, ha="right", fontsize=8)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#444")
    ax.set_title("Comparação de Missões", color="white", fontsize=12, pad=10)
    ax.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)

    plt.tight_layout()
    plt.show()
    return filename
