from typing import Dict, Tuple, Optional, List
from models.graph import Graph


def floyd_warshall(graph: Graph) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
    nodes = graph.get_all_nodes()
    n = len(nodes)
    
    # Inicializar matrices de distancia y siguiente nodo
    dist: Dict[Tuple[str, str], float] = {}
    next_node: Dict[Tuple[str, str], Optional[str]] = {}
    
    # Inicializar con infinito
    for i in nodes:
        for j in nodes:
            if i == j:
                dist[(i, j)] = 0
                next_node[(i, j)] = None
            else:
                dist[(i, j)] = float('infinity')
                next_node[(i, j)] = None
    
    # Llenar con las aristas existentes
    for node in nodes:
        for neighbor, weight in graph.get_neighbors(node):
            dist[(node, neighbor)] = weight
            next_node[(node, neighbor)] = neighbor
    
    # Algoritmo principal de Floyd-Warshall
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[(i, k)] + dist[(k, j)] < dist[(i, j)]:
                    dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
                    next_node[(i, j)] = next_node[(i, k)]
    
    return dist, next_node


def get_path_floyd_warshall(
    next_node: Dict[Tuple[str, str], Optional[str]], 
    start: str, 
    end: str
) -> Optional[List[str]]:

    if next_node.get((start, end)) is None:
        return None
    
    path = [start]
    current = start
    
    while current != end:
        current = next_node[(current, end)]
        if current is None:
            return None
        path.append(current)
    
    return path
