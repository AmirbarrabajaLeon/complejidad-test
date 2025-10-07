"""
Generador de datasets para grafos de ciudades simuladas.
Genera grafos con estructura realista de calles y distancias.
"""

import random
import csv
import json
import math
from typing import List, Tuple, Set


class CityGraphGenerator:
    """
    Generador de grafos que simulan redes de calles de una ciudad.
    """
    
    def __init__(self, num_nodes: int = 1500, seed: int = None):
        """
        Inicializa el generador.
        
        Args:
            num_nodes: Número de nodos a generar
            seed: Semilla para reproducibilidad (opcional)
        """
        self.num_nodes = num_nodes
        if seed is not None:
            random.seed(seed)
    
    def generate_grid_based_city(self) -> List[Tuple[str, str, float]]:
        """
        Genera un grafo basado en una cuadrícula con algunas conexiones diagonales.
        Simula una ciudad con calles organizadas en bloques.
        
        Returns:
            List[Tuple[str, str, float]]: Lista de aristas (origen, destino, distancia)
        """
        edges = []
        
        # Calcular dimensiones de la cuadrícula
        grid_size = int(math.sqrt(self.num_nodes)) + 1
        
        # Generar nodos en cuadrícula con algo de aleatoriedad
        nodes = []
        for i in range(grid_size):
            for j in range(grid_size):
                if len(nodes) >= self.num_nodes:
                    break
                node_id = f"N{i}_{j}"
                x = i * 100 + random.uniform(-10, 10)
                y = j * 100 + random.uniform(-10, 10)
                nodes.append((node_id, x, y))
            if len(nodes) >= self.num_nodes:
                break
        
        # Crear diccionario de posiciones
        positions = {node[0]: (node[1], node[2]) for node in nodes}
        
        # Generar conexiones horizontales y verticales
        for i in range(grid_size):
            for j in range(grid_size):
                current = f"N{i}_{j}"
                if current not in positions:
                    continue
                
                # Conexión hacia la derecha
                right = f"N{i}_{j+1}"
                if right in positions:
                    dist = self._calculate_distance(positions[current], positions[right])
                    edges.append((current, right, dist))
                    # Hacer algunas calles bidireccionales
                    if random.random() > 0.3:
                        edges.append((right, current, dist * random.uniform(0.9, 1.1)))
                
                # Conexión hacia abajo
                down = f"N{i+1}_{j}"
                if down in positions:
                    dist = self._calculate_distance(positions[current], positions[down])
                    edges.append((current, down, dist))
                    if random.random() > 0.3:
                        edges.append((down, current, dist * random.uniform(0.9, 1.1)))
                
                # Algunas conexiones diagonales (avenidas)
                if random.random() > 0.7:
                    diag = f"N{i+1}_{j+1}"
                    if diag in positions:
                        dist = self._calculate_distance(positions[current], positions[diag])
                        edges.append((current, diag, dist))
        
        # Agregar algunas conexiones de largo alcance (autopistas)
        num_highways = self.num_nodes // 50
        for _ in range(num_highways):
            node1 = random.choice(nodes)[0]
            node2 = random.choice(nodes)[0]
            if node1 != node2:
                dist = self._calculate_distance(positions[node1], positions[node2]) * 0.6
                edges.append((node1, node2, dist))
        
        return edges
    
    def generate_random_city(self, avg_connections: int = 4) -> List[Tuple[str, str, float]]:
        """
        Genera un grafo aleatorio con distribución más realista.
        
        Args:
            avg_connections: Número promedio de conexiones por nodo
            
        Returns:
            List[Tuple[str, str, float]]: Lista de aristas (origen, destino, distancia)
        """
        edges = []
        
        # Generar posiciones aleatorias para los nodos
        nodes = []
        for i in range(self.num_nodes):
            node_id = f"N{i}"
            x = random.uniform(0, 1000)
            y = random.uniform(0, 1000)
            nodes.append((node_id, x, y))
        
        positions = {node[0]: (node[1], node[2]) for node in nodes}
        
        # Para cada nodo, conectar con los k vecinos más cercanos
        for node_id, x, y in nodes:
            # Calcular distancias a todos los otros nodos
            distances = []
            for other_id, other_x, other_y in nodes:
                if node_id != other_id:
                    dist = math.sqrt((x - other_x)**2 + (y - other_y)**2)
                    distances.append((other_id, dist))
            
            # Ordenar por distancia y tomar los k más cercanos
            distances.sort(key=lambda x: x[1])
            k = random.randint(avg_connections - 1, avg_connections + 2)
            
            for neighbor_id, dist in distances[:k]:
                # Agregar algo de variación a la distancia
                actual_dist = dist * random.uniform(0.8, 1.2)
                edges.append((node_id, neighbor_id, round(actual_dist, 2)))
        
        return edges
    
    def generate_clustered_city(self, num_clusters: int = 10) -> List[Tuple[str, str, float]]:
        """
        Genera un grafo con estructura de clusters (barrios).
        Simula una ciudad con diferentes zonas conectadas entre sí.
        
        Args:
            num_clusters: Número de clusters (barrios)
            
        Returns:
            List[Tuple[str, str, float]]: Lista de aristas (origen, destino, distancia)
        """
        edges = []
        nodes_per_cluster = self.num_nodes // num_clusters
        
        # Generar clusters
        all_nodes = []
        cluster_centers = []
        
        for cluster_id in range(num_clusters):
            # Centro del cluster
            center_x = random.uniform(100, 900)
            center_y = random.uniform(100, 900)
            cluster_centers.append((center_x, center_y))
            
            # Nodos dentro del cluster
            cluster_nodes = []
            for i in range(nodes_per_cluster):
                node_id = f"C{cluster_id}_N{i}"
                # Distribución alrededor del centro
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, 50)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                cluster_nodes.append((node_id, x, y))
                all_nodes.append((node_id, x, y, cluster_id))
            
            # Conectar nodos dentro del cluster
            for i, (node_id, x, y) in enumerate(cluster_nodes):
                # Conectar con 3-5 nodos cercanos en el mismo cluster
                num_connections = random.randint(3, 5)
                for j in range(num_connections):
                    other_idx = random.randint(0, len(cluster_nodes) - 1)
                    if i != other_idx:
                        other_id, other_x, other_y = cluster_nodes[other_idx]
                        dist = math.sqrt((x - other_x)**2 + (y - other_y)**2)
                        edges.append((node_id, other_id, round(dist, 2)))
        
        # Conectar clusters entre sí (carreteras principales)
        for cluster_id in range(num_clusters):
            # Conectar con 2-3 clusters vecinos
            num_connections = random.randint(2, 3)
            for _ in range(num_connections):
                other_cluster = random.randint(0, num_clusters - 1)
                if cluster_id != other_cluster:
                    # Seleccionar nodos aleatorios de cada cluster
                    node1 = random.choice([n for n in all_nodes if n[3] == cluster_id])
                    node2 = random.choice([n for n in all_nodes if n[3] == other_cluster])
                    
                    dist = math.sqrt((node1[1] - node2[1])**2 + (node1[2] - node2[2])**2)
                    edges.append((node1[0], node2[0], round(dist, 2)))
        
        return edges
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calcula la distancia euclidiana entre dos posiciones.
        
        Args:
            pos1: Posición (x, y) del primer punto
            pos2: Posición (x, y) del segundo punto
            
        Returns:
            float: Distancia redondeada a 2 decimales
        """
        return round(math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2), 2)
    
    def save_to_csv(self, edges: List[Tuple[str, str, float]], filepath: str):
        """
        Guarda las aristas en un archivo CSV.
        
        Args:
            edges: Lista de aristas
            filepath: Ruta del archivo de salida
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['origen', 'destino', 'distancia'])
            for source, destination, weight in edges:
                writer.writerow([source, destination, weight])
    
    def save_to_json(self, edges: List[Tuple[str, str, float]], filepath: str):
        """
        Guarda las aristas en un archivo JSON.
        
        Args:
            edges: Lista de aristas
            filepath: Ruta del archivo de salida
        """
        data = {
            'edges': [
                {'source': src, 'destination': dst, 'weight': wgt}
                for src, dst, wgt in edges
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    """
    Función principal para generar datasets de ejemplo.
    """
    print("=== Generador de Datasets para Sistema de Rutas ===\n")
    
    # Generar dataset con estructura de cuadrícula
    print("Generando dataset con estructura de cuadrícula (1500 nodos)...")
    generator = CityGraphGenerator(num_nodes=1500, seed=42)
    edges = generator.generate_grid_based_city()
    generator.save_to_csv(edges, 'data/city_grid_1500.csv')
    print(f"✓ Generado: city_grid_1500.csv ({len(edges)} aristas)")
    
    # Generar dataset con clusters
    print("\nGenerando dataset con estructura de clusters (1500 nodos)...")
    generator = CityGraphGenerator(num_nodes=1500, seed=42)
    edges = generator.generate_clustered_city(num_clusters=15)
    generator.save_to_csv(edges, 'data/city_clustered_1500.csv')
    print(f"✓ Generado: city_clustered_1500.csv ({len(edges)} aristas)")
    
    # Generar dataset aleatorio
    print("\nGenerando dataset aleatorio (1500 nodos)...")
    generator = CityGraphGenerator(num_nodes=1500, seed=42)
    edges = generator.generate_random_city(avg_connections=4)
    generator.save_to_csv(edges, 'data/city_random_1500.csv')
    print(f"✓ Generado: city_random_1500.csv ({len(edges)} aristas)")
    
    # Generar dataset pequeño para pruebas
    print("\nGenerando dataset pequeño para pruebas (50 nodos)...")
    generator = CityGraphGenerator(num_nodes=50, seed=42)
    edges = generator.generate_grid_based_city()
    generator.save_to_csv(edges, 'data/city_test_50.csv')
    generator.save_to_json(edges, 'data/city_test_50.json')
    print(f"✓ Generado: city_test_50.csv y city_test_50.json ({len(edges)} aristas)")
    
    print("\n¡Datasets generados exitosamente!")


if __name__ == '__main__':
    main()
