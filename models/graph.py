"""
Implementación de estructuras de datos para grafos dirigidos y ponderados.
"""

from typing import Dict, List, Tuple, Optional
import json
import csv


class Node:
    """
    Representa un nodo en el grafo (punto en la ciudad).
    
    Attributes:
        id (str): Identificador único del nodo
        name (str): Nombre descriptivo del nodo
        x (float): Coordenada X (opcional, para visualización)
        y (float): Coordenada Y (opcional, para visualización)
    """
    
    def __init__(self, node_id: str, name: str = None, x: float = 0, y: float = 0):
        """
        Inicializa un nodo.
        
        Args:
            node_id: Identificador único del nodo
            name: Nombre descriptivo (opcional)
            x: Coordenada X (opcional)
            y: Coordenada Y (opcional)
        """
        self.id = node_id
        self.name = name if name else node_id
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Node({self.id})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)


class Graph:
    """
    Implementación de un grafo dirigido y ponderado.
    
    Attributes:
        nodes (Dict[str, Node]): Diccionario de nodos indexados por ID
        edges (Dict[str, List[Tuple[str, float]]]): Lista de adyacencia con pesos
    """
    
    def __init__(self):
        """Inicializa un grafo vacío."""
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Tuple[str, float]]] = {}
        self.metadata: Dict[str, Dict] = {}  # Metadata adicional por nodo
    
    def add_node(self, node_id: str, name: str = None, x: float = 0, y: float = 0) -> Node:
        """
        Agrega un nodo al grafo.
        
        Args:
            node_id: Identificador único del nodo
            name: Nombre descriptivo (opcional)
            x: Coordenada X (opcional)
            y: Coordenada Y (opcional)
            
        Returns:
            Node: El nodo creado o existente
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, name, x, y)
            self.edges[node_id] = []
        return self.nodes[node_id]
    
    def add_edge(self, source: str, destination: str, weight: float):
        """
        Agrega una arista dirigida con peso al grafo.
        
        Args:
            source: ID del nodo origen
            destination: ID del nodo destino
            weight: Peso de la arista (distancia)
        """
        # Asegurar que ambos nodos existen
        if source not in self.nodes:
            self.add_node(source)
        if destination not in self.nodes:
            self.add_node(destination)
        
        # Agregar la arista
        self.edges[source].append((destination, weight))
    
    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """
        Obtiene los vecinos de un nodo con sus pesos.
        
        Args:
            node_id: ID del nodo
            
        Returns:
            List[Tuple[str, float]]: Lista de tuplas (vecino_id, peso)
        """
        return self.edges.get(node_id, [])
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Obtiene un nodo por su ID.
        
        Args:
            node_id: ID del nodo
            
        Returns:
            Node: El nodo si existe, None en caso contrario
        """
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[str]:
        """
        Obtiene la lista de todos los IDs de nodos.
        
        Returns:
            List[str]: Lista de IDs de nodos
        """
        return list(self.nodes.keys())
    
    def node_exists(self, node_id: str) -> bool:
        """
        Verifica si un nodo existe en el grafo.
        
        Args:
            node_id: ID del nodo
            
        Returns:
            bool: True si el nodo existe, False en caso contrario
        """
        return node_id in self.nodes
    
    def get_edge_weight(self, source: str, destination: str) -> Optional[float]:
        """
        Obtiene el peso de una arista específica.
        
        Args:
            source: ID del nodo origen
            destination: ID del nodo destino
            
        Returns:
            float: Peso de la arista si existe, None en caso contrario
        """
        if source in self.edges:
            for neighbor, weight in self.edges[source]:
                if neighbor == destination:
                    return weight
        return None
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del grafo.
        
        Returns:
            Dict: Diccionario con estadísticas del grafo
        """
        total_edges = sum(len(neighbors) for neighbors in self.edges.values())
        return {
            'num_nodes': len(self.nodes),
            'num_edges': total_edges,
            'avg_degree': total_edges / len(self.nodes) if self.nodes else 0
        }
    
    def load_from_csv(self, filepath: str) -> int:
        """
        Carga el grafo desde un archivo CSV simple.
        
        Formato esperado: origen,destino,distancia
        
        NOTA: Para archivos GDELT, usa load_from_gdelt() en su lugar.
        
        Args:
            filepath: Ruta al archivo CSV
            
        Returns:
            int: Número de aristas cargadas
        """
        edges_loaded = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Saltar encabezado si existe
                
                for row in reader:
                    if len(row) >= 3:
                        source, destination, weight = row[0].strip(), row[1].strip(), float(row[2].strip())
                        self.add_edge(source, destination, weight)
                        edges_loaded += 1
        except Exception as e:
            # Detectar si es un archivo GDELT
            if 'could not convert string to float' in str(e) and '\t' in str(e):
                # Verificar si es el archivo GDELT específico
                is_gdelt_file = '20251004' in filepath or 'export' in filepath.lower()
                
                error_msg = (
                    f"\n{'='*70}\n"
                    f"❌ ERROR: Este es un archivo GDELT, no un CSV simple\n"
                    f"{'='*70}\n\n"
                )
                
                if is_gdelt_file:
                    error_msg += (
                        f"El archivo '{filepath}' es un dataset GDELT con 58 columnas.\n\n"
                        f"SOLUCIÓN:\n"
                        f"  1. Vuelve al menú principal\n"
                        f"  2. Selecciona la opción 3: 'Cargar dataset GDELT'\n"
                        f"  3. Ingresa el nombre del archivo: {os.path.basename(filepath)}\n"
                        f"  4. Configura los filtros (país, eventos, distancia)\n\n"
                    )
                else:
                    error_msg += (
                        f"Este archivo parece ser GDELT (TSV con múltiples columnas).\n\n"
                        f"Por favor usa la opción 3 del menú: 'Cargar dataset GDELT'\n"
                        f"en lugar de la opción 1.\n\n"
                    )
                
                error_msg += (
                    f"DIFERENCIA:\n"
                    f"  • Opción 1: Para CSV simples (origen,destino,distancia)\n"
                    f"  • Opción 3: Para archivos GDELT (58 columnas con tabuladores)\n\n"
                    f"{'='*70}\n"
                )
                
                raise Exception(error_msg)
            raise Exception(f"Error al cargar el archivo CSV: {str(e)}")
        
        return edges_loaded
    
    def load_from_json(self, filepath: str) -> int:
        """
        Carga el grafo desde un archivo JSON.
        
        Formato esperado: 
        {
            "edges": [
                {"source": "A", "destination": "B", "weight": 5},
                ...
            ]
        }
        
        Args:
            filepath: Ruta al archivo JSON
            
        Returns:
            int: Número de aristas cargadas
        """
        edges_loaded = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                if 'edges' in data:
                    for edge in data['edges']:
                        source = edge['source']
                        destination = edge['destination']
                        weight = float(edge['weight'])
                        self.add_edge(source, destination, weight)
                        edges_loaded += 1
        except Exception as e:
            raise Exception(f"Error al cargar el archivo JSON: {str(e)}")
        
        return edges_loaded
    
    def save_to_csv(self, filepath: str):
        """
        Guarda el grafo en un archivo CSV.
        
        Args:
            filepath: Ruta al archivo CSV de salida
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['origen', 'destino', 'distancia'])
                
                for source, neighbors in self.edges.items():
                    for destination, weight in neighbors:
                        writer.writerow([source, destination, weight])
        except Exception as e:
            raise Exception(f"Error al guardar el archivo CSV: {str(e)}")
    
    def load_from_gdelt(self, filepath: str, country_filter: Optional[str] = None, 
                       max_rows: Optional[int] = None, max_distance: float = 1000.0) -> int:
        """
        Carga el grafo desde un archivo GDELT.
        
        Args:
            filepath: Ruta al archivo GDELT (TSV)
            country_filter: Código de país para filtrar (ej: 'USA', 'CAN')
            max_rows: Número máximo de filas a procesar
            max_distance: Distancia máxima para crear aristas (km)
            
        Returns:
            int: Número de aristas cargadas
        """
        try:
            from data.gdelt_parser import GDELTParser
            
            parser = GDELTParser(filepath)
            events_parsed = parser.parse(max_rows=max_rows)
            
            if events_parsed == 0:
                raise Exception("No se pudieron parsear eventos del archivo")
            
            # Construir aristas basadas en proximidad geográfica
            edges = parser.build_graph_edges(
                country_filter=country_filter,
                max_distance=max_distance
            )
            
            # Agregar nodos y aristas al grafo
            for event in parser.events:
                if country_filter and country_filter.upper() not in event.get_country_codes():
                    continue
                
                # Agregar nodo con coordenadas
                self.add_node(
                    node_id=event.event_id,
                    name=event.get_display_name(),
                    x=event.longitude,
                    y=event.latitude
                )
                
                # Guardar metadata del evento
                self.metadata[event.event_id] = {
                    'date': event.event_date,
                    'actor1': event.actor1_name,
                    'actor2': event.actor2_name,
                    'location': event.location_name,
                    'country': event.location_country,
                    'goldstein': event.goldstein_scale,
                    'url': event.url
                }
            
            # Agregar aristas
            edges_loaded = 0
            for source, destination, weight in edges:
                self.add_edge(source, destination, weight)
                edges_loaded += 1
            
            return edges_loaded
            
        except Exception as e:
            raise Exception(f"Error al cargar archivo GDELT: {str(e)}")
    
    def get_node_metadata(self, node_id: str) -> Optional[Dict]:
        """
        Obtiene la metadata de un nodo.
        
        Args:
            node_id: ID del nodo
            
        Returns:
            Dict: Metadata del nodo o None
        """
        return self.metadata.get(node_id)
    
    def search_nodes(self, query: str, limit: int = 50) -> List[str]:
        """
        Busca nodos por nombre o ID.
        
        Args:
            query: Texto a buscar
            limit: Número máximo de resultados
            
        Returns:
            List[str]: Lista de IDs de nodos que coinciden
        """
        query_lower = query.lower()
        results = []
        
        for node_id, node in self.nodes.items():
            if len(results) >= limit:
                break
            
            # Buscar en ID y nombre
            if query_lower in node_id.lower() or query_lower in node.name.lower():
                results.append(node_id)
            # Buscar en metadata
            elif node_id in self.metadata:
                meta = self.metadata[node_id]
                if any(query_lower in str(v).lower() for v in meta.values()):
                    results.append(node_id)
        
        return results
    
    def filter_nodes_by_country(self, country_code: str) -> List[str]:
        """
        Filtra nodos por código de país.
        
        Args:
            country_code: Código de país (ej: 'USA')
            
        Returns:
            List[str]: Lista de IDs de nodos del país
        """
        results = []
        country_upper = country_code.upper()
        
        for node_id in self.nodes.keys():
            if node_id in self.metadata:
                if self.metadata[node_id].get('country', '').upper() == country_upper:
                    results.append(node_id)
        
        return results
    
    def __str__(self):
        stats = self.get_stats()
        return f"Graph(nodes={stats['num_nodes']}, edges={stats['num_edges']})"
    
    def __repr__(self):
        return self.__str__()
