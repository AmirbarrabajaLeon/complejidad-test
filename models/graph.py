from typing import Dict, List, Tuple, Optional
import json
import csv
import datetime
import time


# ### NUEVO: Necesitamos esto para manejar las fechas en el Eje X
def date_to_timestamp(date_str: str) -> float:
    """Convierte string de fecha a timestamp (float) para el eje X"""
    try:
        # Intenta formatos comunes. Ajusta según tu dataset
        # Formato HuffPost: 2022-09-23
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.timestamp()
    except ValueError:
        return 0.0


class Node:
    # ### MODIFICADO: Añadimos 'date' y 'content'
    def __init__(self, node_id: str, name: str = None, content: str = "", date: str = "", x: float = 0, y: float = 0, tone: int = 0):
        self.id = node_id
        self.name = name if name else node_id
        self.content = content  # ### NUEVO: El texto de la noticia para comparar similitud
        self.date = date  # ### NUEVO: La fecha original (string)
        self.tone = tone  # <--- NUEVO

        # TRUCO PARA LA GUI:
        # Si x es 0 y tenemos fecha, usamos la fecha como posición X.
        if x == 0 and date:
            self.x = date_to_timestamp(date)
        else:
            self.x = x

        self.y = y

    def __str__(self):
        return f"Node({self.id} | {self.date})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


class Graph:

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Tuple[str, float]]] = {}
        self.metadata: Dict[str, Dict] = {}

        # ### MODIFICADO: Ahora acepta content y date

    def add_node(self, node_id: str, name: str = None, content: str = "", date: str = "", x: float = 0,
                 y: float = 0, tone: int = 0) -> Node:
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, name, content, date, x, y, tone)
            self.edges[node_id] = []
        return self.nodes[node_id]

    def add_edge(self, source: str, destination: str, weight: float):
        # Aseguramos que existan, si no, se crean vacíos (cuidado aquí)
        if source not in self.nodes:
            self.add_node(source)
        if destination not in self.nodes:
            self.add_node(destination)

        # Evitar duplicados
        for dest, w in self.edges[source]:
            if dest == destination:
                return  # Ya existe la arista

        self.edges[source].append((destination, weight))
        # Si el grafo es no dirigido (similitud A-B es igual a B-A), descomenta esto:
        # self.edges[destination].append((source, weight))

    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        return self.edges.get(node_id, [])

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    def get_stats(self) -> Dict:
        total_edges = sum(len(neighbors) for neighbors in self.edges.values())
        return {
            'num_nodes': len(self.nodes),
            'num_edges': total_edges,
            'avg_degree': total_edges / len(self.nodes) if self.nodes else 0
        }

    # ### NUEVO: Función genérica para cargar tu dataset de noticias
    # Esta función reemplaza la lógica compleja de GDELT/CSV anterior
    def load_from_news_dataset(self, data_list: List[Dict]):
        """
        Carga nodos desde una lista de diccionarios (procesada previamente).
        data_list debe ser: [{'id': '1', 'headline': '...', 'date': '...', 'content': '...'}, ...]
        """
        import random
        for item in data_list:
            # Asignamos Y aleatorio para que no se solapen visualmente en la línea de tiempo
            random_y = random.uniform(0, 100)

            self.add_node(
                node_id=str(item['id']),
                name=item['headline'],
                content=item.get('short_description', '') or item.get('content', ''),
                date=item['date'],
                y=random_y,
                tone=item.get('tone', 0)  # <--- LEEMOS EL TONO
            )
        print(f"✅ Grafo cargado con {len(self.nodes)} noticias.")

    # Mantenemos métodos auxiliares por si la GUI los usa
    def get_edge_weight(self, source: str, destination: str) -> Optional[float]:
        if source in self.edges:
            for neighbor, weight in self.edges[source]:
                if neighbor == destination:
                    return weight
        return None