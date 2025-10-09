from typing import Dict, List, Tuple, Optional
from models.graph import Graph


def bellman_ford(graph: Graph, start: str, end: str) -> Tuple[Optional[float], Optional[List[str]], bool]:
    if not graph.node_exists(start):
        raise ValueError(f"El nodo inicial '{start}' no existe en el grafo")
    if not graph.node_exists(end):
        raise ValueError(f"El nodo final '{end}' no existe en el grafo")
    
    nodes = graph.get_all_nodes()
    distances: Dict[str, float] = {node: float('infinity') for node in nodes}
    distances[start] = 0
    
    previous: Dict[str, Optional[str]] = {node: None for node in nodes}

    for _ in range(len(nodes) - 1):
        for node in nodes:
            if distances[node] == float('infinity'):
                continue
            
            for neighbor, weight in graph.get_neighbors(node):
                if distances[node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[node] + weight
                    previous[neighbor] = node

    has_negative_cycle = False
    for node in nodes:
        if distances[node] == float('infinity'):
            continue
        
        for neighbor, weight in graph.get_neighbors(node):
            if distances[node] + weight < distances[neighbor]:
                has_negative_cycle = True
                break
        
        if has_negative_cycle:
            break

    if has_negative_cycle:
        return None, None, True

    if distances[end] == float('infinity'):
        return None, None, False
    
    path = _reconstruct_path(previous, start, end)
    return distances[end], path, False



def _reconstruct_path(previous: Dict[str, Optional[str]], start: str, end: str) -> List[str]:
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    
    if path[0] != start:
        return []
    
    return path
