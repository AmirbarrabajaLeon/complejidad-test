"""
Implementación del algoritmo de Bellman-Ford para encontrar el camino más corto.
Soporta grafos con pesos negativos y detecta ciclos negativos.
"""

from typing import Dict, List, Tuple, Optional
from models.graph import Graph


def bellman_ford(graph: Graph, start: str, end: str) -> Tuple[Optional[float], Optional[List[str]], bool]:
    """
    Implementa el algoritmo de Bellman-Ford para encontrar el camino más corto.
    
    El algoritmo de Bellman-Ford puede manejar aristas con pesos negativos
    y detectar ciclos negativos. Es más lento que Dijkstra pero más versátil.
    
    Complejidad temporal: O(V * E) donde V es el número de vértices y E el número de aristas
    Complejidad espacial: O(V)
    
    Args:
        graph: Grafo sobre el cual buscar
        start: ID del nodo inicial
        end: ID del nodo final
        
    Returns:
        Tuple[Optional[float], Optional[List[str]], bool]:
            - Distancia total del camino más corto (None si no existe o hay ciclo negativo)
            - Lista de nodos en el camino (None si no existe o hay ciclo negativo)
            - True si se detectó un ciclo negativo, False en caso contrario
    """
    # Validar que los nodos existen
    if not graph.node_exists(start):
        raise ValueError(f"El nodo inicial '{start}' no existe en el grafo")
    if not graph.node_exists(end):
        raise ValueError(f"El nodo final '{end}' no existe en el grafo")
    
    # Inicializar estructuras de datos
    nodes = graph.get_all_nodes()
    distances: Dict[str, float] = {node: float('infinity') for node in nodes}
    distances[start] = 0
    
    previous: Dict[str, Optional[str]] = {node: None for node in nodes}
    
    # Relajar aristas V-1 veces
    for _ in range(len(nodes) - 1):
        for node in nodes:
            if distances[node] == float('infinity'):
                continue
            
            for neighbor, weight in graph.get_neighbors(node):
                if distances[node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[node] + weight
                    previous[neighbor] = node
    
    # Verificar ciclos negativos
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
    
    # Si hay ciclo negativo, retornar None
    if has_negative_cycle:
        return None, None, True
    
    # Reconstruir el camino
    if distances[end] == float('infinity'):
        return None, None, False
    
    path = _reconstruct_path(previous, start, end)
    return distances[end], path, False


def _reconstruct_path(previous: Dict[str, Optional[str]], start: str, end: str) -> List[str]:
    """
    Reconstruye el camino desde el nodo inicial al final.
    
    Args:
        previous: Diccionario de predecesores
        start: Nodo inicial
        end: Nodo final
        
    Returns:
        List[str]: Lista de nodos en el camino
    """
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    
    if path[0] != start:
        return []
    
    return path
