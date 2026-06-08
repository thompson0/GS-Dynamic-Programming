"""
Módulo: models.py
Definição dos modelos de dados do projeto.
"""

from dataclasses import dataclass, field
from data_structures import LinkedList


@dataclass(frozen=True)
class Body:
    name: str
    body_type: str
    distance_mkm: float
    gravity: float


@dataclass(frozen=True)
class Mission:
    origin: str
    destination: str
    priority: int = 1  


@dataclass
class GraphEdge:
    """Aresta do grafo de rotas com critérios múltiplos."""
    destination: Body
    distance_mkm: float
    travel_time_days: float
    fuel_cost: float         
    gravity_penalty: float   


@dataclass
class Route:
    path: LinkedList
    distance_mkm: float
    travel_time_days: float
    fuel_cost: float
    score: float
    criteria: dict = field(default_factory=dict)  