"""
Implementación del algoritmo de Dijkstra para encontrar el camino más corto.
"""

import heapq
from typing import Dict, List, Tuple, Optional
from models.graph import Graph


def dijkstra(graph: Graph, start: str, end: str) -> Tuple[Optional[float], Optional[List[str]]]:
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
