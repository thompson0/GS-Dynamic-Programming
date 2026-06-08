"""
Módulo: algorithms.py
Algoritmos de busca e ordenação sobre listas de Body.
  - linear_search
  - binary_search  (requer lista ordenada por distance_mkm)
  - bubble_sort
"""

from models import Body


def linear_search(items: list[Body], name: str) -> Body | None:
    """Busca linear pelo nome do corpo celeste (O(n))."""
    target = name.strip().lower()
    for body in items:
        if body.name.lower() == target:
            return body
    return None


def binary_search(sorted_items: list[Body], distance_mkm: float) -> Body | None:
    """
    Busca binária por distância exata (O(log n)).
    A lista deve estar ordenada por distance_mkm.
    """
    lo, hi = 0, len(sorted_items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = sorted_items[mid].distance_mkm
        if val == distance_mkm:
            return sorted_items[mid]
        elif val < distance_mkm:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def bubble_sort(items: list[Body]) -> list[Body]:
    """Ordenação por distância usando Bubble Sort (O(n²))."""
    sorted_items = items[:]
    n = len(sorted_items)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if sorted_items[j].distance_mkm > sorted_items[j + 1].distance_mkm:
                sorted_items[j], sorted_items[j + 1] = sorted_items[j + 1], sorted_items[j]
                swapped = True
        if not swapped:
            break  # otimização: já ordenado
    return sorted_items
