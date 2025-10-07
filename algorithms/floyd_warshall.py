"""
Implementación del algoritmo de Floyd-Warshall para encontrar todos los caminos más cortos.
"""

from typing import Dict, Tuple, Optional, List
from models.graph import Graph


def floyd_warshall(graph: Graph) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
    """
    Implementa el algoritmo de Floyd-Warshall para encontrar todos los caminos más cortos.
    
    El algoritmo de Floyd-Warshall calcula las distancias más cortas entre todos los pares
    de nodos en el grafo. Es útil cuando se necesitan múltiples consultas de rutas.
    
    Complejidad temporal: O(V³) donde V es el número de vértices
    Complejidad espacial: O(V²)
    
    Args:
        graph: Grafo sobre el cual calcular
        
    Returns:
        Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], Optional[str]]]:
            - Diccionario de distancias mínimas entre cada par de nodos
            - Diccionario de nodos intermedios para reconstruir caminos
    """
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
    """
    Reconstruye el camino entre dos nodos usando la matriz de siguiente nodo.
    
    Args:
        next_node: Diccionario de nodos intermedios de Floyd-Warshall
        start: Nodo inicial
        end: Nodo final
        
    Returns:
        Optional[List[str]]: Lista de nodos en el camino, None si no existe camino
    """
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
