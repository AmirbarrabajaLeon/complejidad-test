"""
Implementación del algoritmo de Dijkstra para encontrar el camino más corto.
"""

import heapq
from typing import Dict, List, Tuple, Optional
from models.graph import Graph


def dijkstra(graph: Graph, start: str, end: str) -> Tuple[Optional[float], Optional[List[str]]]:
    """
    Implementa el algoritmo de Dijkstra para encontrar el camino más corto.
    
    El algoritmo de Dijkstra es un algoritmo de búsqueda de camino más corto
    que funciona en grafos con pesos no negativos. Utiliza una cola de prioridad
    para explorar los nodos en orden de distancia desde el origen.
    
    Complejidad temporal: O((V + E) log V) donde V es el número de vértices y E el número de aristas
    Complejidad espacial: O(V)
    
    Args:
        graph: Grafo sobre el cual buscar
        start: ID del nodo inicial
        end: ID del nodo final
        
    Returns:
        Tuple[Optional[float], Optional[List[str]]]: 
            - Distancia total del camino más corto (None si no existe)
            - Lista de nodos en el camino (None si no existe)
    """
    # Validar que los nodos existen
    if not graph.node_exists(start):
        raise ValueError(f"El nodo inicial '{start}' no existe en el grafo")
    if not graph.node_exists(end):
        raise ValueError(f"El nodo final '{end}' no existe en el grafo")
    
    # Inicializar estructuras de datos
    distances: Dict[str, float] = {node: float('infinity') for node in graph.get_all_nodes()}
    distances[start] = 0
    
    previous: Dict[str, Optional[str]] = {node: None for node in graph.get_all_nodes()}
    
    # Cola de prioridad: (distancia, nodo)
    priority_queue = [(0, start)]
    visited = set()
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Si ya visitamos este nodo, continuar
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # Si llegamos al destino, podemos terminar
        if current_node == end:
            break
        
        # Si la distancia actual es mayor que la registrada, continuar
        if current_distance > distances[current_node]:
            continue
        
        # Explorar vecinos
        for neighbor, weight in graph.get_neighbors(current_node):
            distance = current_distance + weight
            
            # Si encontramos un camino más corto, actualizarlo
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Reconstruir el camino
    if distances[end] == float('infinity'):
        return None, None
    
    path = reconstruct_path(previous, start, end)
    return distances[end], path


def reconstruct_path(previous: Dict[str, Optional[str]], start: str, end: str) -> List[str]:
    """
    Reconstruye el camino desde el nodo inicial al final usando el diccionario de predecesores.
    
    Args:
        previous: Diccionario de predecesores
        start: Nodo inicial
        end: Nodo final
        
    Returns:
        List[str]: Lista de nodos en el camino desde start hasta end
    """
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = previous[current]
    
    path.reverse()
    
    # Verificar que el camino comienza en start
    if path[0] != start:
        return []
    
    return path


def dijkstra_all_paths(graph: Graph, start: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Calcula las distancias más cortas desde un nodo inicial a todos los demás nodos.
    
    Args:
        graph: Grafo sobre el cual buscar
        start: ID del nodo inicial
        
    Returns:
        Tuple[Dict[str, float], Dict[str, Optional[str]]]:
            - Diccionario de distancias mínimas desde start a cada nodo
            - Diccionario de predecesores para reconstruir caminos
    """
    if not graph.node_exists(start):
        raise ValueError(f"El nodo inicial '{start}' no existe en el grafo")
    
    # Inicializar estructuras de datos
    distances: Dict[str, float] = {node: float('infinity') for node in graph.get_all_nodes()}
    distances[start] = 0
    
    previous: Dict[str, Optional[str]] = {node: None for node in graph.get_all_nodes()}
    
    # Cola de prioridad: (distancia, nodo)
    priority_queue = [(0, start)]
    visited = set()
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        if current_distance > distances[current_node]:
            continue
        
        # Explorar vecinos
        for neighbor, weight in graph.get_neighbors(current_node):
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances, previous
