"""
Módulo: data_structures.py
Implementação das estruturas de dados fundamentais:
  - Node
  - LinkedList (lista ligada simples)
  - Stack     (pilha)
  - Queue     (fila)
"""

from dataclasses import dataclass


@dataclass
class Node:
    value: object
    next: "Node | None" = None


class LinkedList:
    """Lista ligada simples com iteração."""

    def __init__(self) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None

    def append(self, value: object) -> None:
        node = Node(value)
        if self.head is None:
            self.head = node
            self.tail = node
            return
        assert self.tail is not None
        self.tail.next = node
        self.tail = node

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __len__(self) -> int:
        count = 0
        for _ in self:
            count += 1
        return count


class Stack:
    """Pilha (LIFO) baseada em lista."""

    def __init__(self) -> None:
        self._items: list[object] = []

    def push(self, value: object) -> None:
        self._items.append(value)

    def pop(self) -> object:
        if not self._items:
            raise IndexError("pilha vazia")
        return self._items.pop()

    def peek(self) -> object:
        if not self._items:
            raise IndexError("pilha vazia")
        return self._items[-1]

    def empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)


class Queue:
    """Fila (FIFO) baseada em lista."""

    def __init__(self) -> None:
        self._items: list[object] = []

    def enqueue(self, value: object) -> None:
        self._items.append(value)

    def dequeue(self) -> object:
        if not self._items:
            raise IndexError("fila vazia")
        return self._items.pop(0)

    def empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)
