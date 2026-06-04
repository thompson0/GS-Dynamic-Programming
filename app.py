from dataclasses import dataclass
from draw import foguete, planeta, abertura
BODY_DATA = {
    "Mercurio": {"body_type": "planet", "distance_mkm": 57.9, "gravity": 3.7},
    "Venus": {"body_type": "planet", "distance_mkm": 108.2, "gravity": 8.87},
    "Terra": {"body_type": "planet", "distance_mkm": 149.6, "gravity": 9.81},
    "Marte": {"body_type": "planet", "distance_mkm": 227.9, "gravity": 3.71},
    "Jupiter": {"body_type": "planet", "distance_mkm": 778.5, "gravity": 24.79},
    "Saturno": {"body_type": "planet", "distance_mkm": 1434.0, "gravity": 10.44},
    "Urano": {"body_type": "planet", "distance_mkm": 2871.0, "gravity": 8.69},
    "Netuno": {"body_type": "planet", "distance_mkm": 4495.1, "gravity": 11.15},
}
print(abertura)

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


@dataclass
class Node:
    value: object
    next: "Node | None" = None


class LinkedList:
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


class Stack:
    def __init__(self) -> None:
        self._items: list[object] = []

    def push(self, value: object) -> None:
        self._items.append(value)

    def pop(self) -> object:
        if not self._items:
            raise IndexError("pilha vazia")
        return self._items.pop()

    def empty(self) -> bool:
        return not self._items


class Queue:
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


@dataclass
class Route:
    path: LinkedList
    distance_mkm: float
    travel_time_days: float
    score: float


ROCKET_PROFILES = {
    "1": ("Falcon 9", 7.9),
    "2": ("Saturn V", 11.2),
    "3": ("Ariane 5", 7.8),
    "4": ("SLS", 10.8),
}


def load_bodies() -> list[Body]:
    bodies: list[Body] = []
    for name, info in BODY_DATA.items():
        bodies.append(
            Body(
                name=name,
                body_type=info["body_type"],
                distance_mkm=info["distance_mkm"],
                gravity=info["gravity"],
            )
        )
    return bodies


def linear_search(items: list[Body], name: str) -> Body | None:
    target = name.strip().lower()
    for body in items:
        if body.name.lower() == target:
            return body
    return None


def bubble_sort(items: list[Body]) -> list[Body]:
    sorted_items = items[:]
    n = len(sorted_items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if sorted_items[j].distance_mkm > sorted_items[j + 1].distance_mkm:
                sorted_items[j], sorted_items[j + 1] = sorted_items[j + 1], sorted_items[j]
    return sorted_items


def km_s_to_mkm_per_day(speed_km_s: float) -> float:
    return speed_km_s * 86400 / 1_000_000


def build_route(origin: Body, destination: Body, bodies: list[Body], rocket_speed_mkm_per_day: float) -> Route:
    best_path = LinkedList()
    best_path.append(origin)
    best_path.append(destination)
    best_distance = abs(destination.distance_mkm - origin.distance_mkm)
    best_time = best_distance / rocket_speed_mkm_per_day
    best_score = best_distance + best_time

    for body in bodies:
        if body.name in {origin.name, destination.name}:
            continue
        candidate_distance = abs(body.distance_mkm - origin.distance_mkm) + abs(
            destination.distance_mkm - body.distance_mkm
        )
        candidate_time = candidate_distance / rocket_speed_mkm_per_day
        candidate_score = candidate_distance + candidate_time
        if candidate_score < best_score:
            candidate_path = LinkedList()
            candidate_path.append(origin)
            candidate_path.append(body)
            candidate_path.append(destination)
            best_path = candidate_path
            best_distance = candidate_distance
            best_time = candidate_time
            best_score = candidate_score

    return Route(best_path, round(best_distance, 2), round(best_time, 2), round(best_score, 2))


def route_to_text(route: Route) -> str:
    names = [body.name for body in route.path]
    return " -> ".join(names)


def print_body(body: Body) -> None:
    print(f"- {body.name} | {body.body_type} | distancia {body.distance_mkm} Mkm | gravidade {body.gravity} m/s2")


def print_route(route: Route) -> None:
    print(f"[INFO] rota: {route_to_text(route)}")
    print(f"[INFO] distancia: {route.distance_mkm} Mkm")
    print(f"[INFO] tempo estimado: {route.travel_time_days} dias")
    print(f"[INFO] score: {route.score}")


def choose_rocket() -> tuple[str, float]:
    print(foguete)
    print("\nEscolha um foguete:")
    for key, (name, speed_km_s) in ROCKET_PROFILES.items():
        print(f"{key} - {name} ({speed_km_s} km/s)")
    choice = input("Opcao: ").strip()
    rocket = ROCKET_PROFILES.get(choice)
    if rocket is None:
        raise ValueError("foguete invalido")
    name, speed_km_s = rocket
    return name, km_s_to_mkm_per_day(speed_km_s)


def main() -> None:
    bodies = load_bodies()
    if not bodies:
        return

    missions = Queue()
    history = Stack()
    rocket_name = "Falcon 9"
    rocket_speed_mkm_per_day = km_s_to_mkm_per_day(7.9)

    print("[INFO] Planejador de rota iniciado")

    while True:
        print()
        print("1 - Listar corpos")
        print("2 - Buscar corpo")
        print("3 - Calcular rota")
        print("4 - Enfileirar missao")
        print("5 - Processar fila")
        print("6 - Desfazer ultima rota")
        print("7 - Escolher velocidade do foguete")
        print("0 - Sair")
        print(f"[INFO] foguete atual: {rocket_name}")

        choice = input("Opcao: ").strip()

        try:
            if choice == "1":
                print(planeta)
                for body in bubble_sort(bodies):
                    print_body(body)

            elif choice == "2":
                name = input("Nome: ").strip()
                body = linear_search(bodies, name)
                if body is None:
                    print("[INFO] corpo nao encontrado")
                else:
                    print_body(body)

            elif choice == "3":
                origin_name = input("Origem: ").strip()
                destination_name = input("Destino: ").strip()
                origin = linear_search(bodies, origin_name)
                destination = linear_search(bodies, destination_name)
                if origin is None or destination is None:
                    print("[ERRO] origem ou destino invalido")
                    continue
                if origin.name == destination.name:
                    print("[ERRO] origem e destino devem ser diferentes")
                    continue
                route = build_route(origin, destination, bodies, rocket_speed_mkm_per_day)
                history.push(route)
                print_route(route)

            elif choice == "4":
                origin_name = input("Origem: ").strip()
                destination_name = input("Destino: ").strip()
                missions.enqueue(Mission(origin_name, destination_name))
                print("[INFO] missao adicionada na fila")

            elif choice == "5":
                if missions.empty():
                    print("[INFO] fila vazia")
                    continue
                while not missions.empty():
                    mission = missions.dequeue()
                    origin = linear_search(bodies, mission.origin)
                    destination = linear_search(bodies, mission.destination)
                    if origin is None or destination is None:
                        print(f"[ERRO] missao invalida: {mission.origin} -> {mission.destination}")
                        continue
                    route = build_route(origin, destination, bodies, rocket_speed_mkm_per_day)
                    history.push(route)
                    print(f"[INFO] {mission.origin} -> {mission.destination}")
                    print_route(route)

            elif choice == "6":
                if history.empty():
                    print("[INFO] nada para desfazer")
                else:
                    route = history.pop()
                    print(f"[INFO] rota removida: {route_to_text(route)}")

            elif choice == "7":
                rocket_name, rocket_speed_mkm_per_day = choose_rocket()
                print(f"[INFO] foguete selecionado: {rocket_name}")
                print(f"[INFO] velocidade usada no calculo: {rocket_speed_mkm_per_day:.4f} Mkm/dia")

            elif choice == "0":
                print("[INFO] encerrando")
                break

            else:
                print("[AVISO] opcao invalida")

        except (IndexError, ValueError) as exc:
            print(f"[ERRO] {exc}")


if __name__ == "__main__":
    main()
