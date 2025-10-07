"""
Sistema de Búsqueda de Rutas Óptimas
Aplicación de consola para calcular rutas más cortas entre puntos de una ciudad.

Curso: Complejidad Algorítmica 1ACC0184
Trabajo: TB1-TB2
"""

import os
import sys
import time
from typing import Optional

from models.graph import Graph
from algorithms.dijkstra import dijkstra, dijkstra_all_paths
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, get_path_floyd_warshall


class RouteFinderApp:
    """
    Aplicación principal para el sistema de búsqueda de rutas óptimas.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.graph: Optional[Graph] = None
        self.dataset_loaded = False
        self.last_path = None  # Guardar última ruta encontrada para visualización
    
    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprime el encabezado de la aplicación."""
        print("=" * 70)
        print(" " * 15 + "SISTEMA DE RUTAS ÓPTIMAS")
        print(" " * 10 + "Búsqueda de Caminos Más Cortos en Grafos")
        print("=" * 70)
        print()
    
    def print_menu(self):
        """Imprime el menú principal."""
        print("\n" + "─" * 70)
        print("MENÚ PRINCIPAL")
        print("─" * 70)
        print("1. Cargar dataset desde archivo CSV")
        print("2. Cargar dataset desde archivo JSON")
        print("3. Cargar dataset GDELT (eventos geopolíticos)")
        print("4. Generar dataset aleatorio")
        print("5. Buscar nodos (por ID, país, ubicación)")
        print("6. Buscar ruta más corta (Dijkstra)")
        print("7. Buscar ruta más corta (Bellman-Ford)")
        print("8. Calcular todas las rutas (Floyd-Warshall)")
        print("9. Mostrar estadísticas del grafo")
        print("10. Listar algunos nodos disponibles")
        print("11. Ejecutar pruebas de rendimiento")
        print("12. Visualizar grafo (Graphviz)")
        print("13. Visualizar ruta encontrada (Graphviz)")
        print("0. Salir")
        print("─" * 70)
    
    def load_csv_dataset(self):
        """Carga un dataset desde un archivo CSV."""
        print("\n" + "─" * 70)
        print("CARGAR DATASET CSV SIMPLE")
        print("─" * 70)
        
        print("\n⚠️  IMPORTANTE:")
        print("   Esta opción es para archivos CSV simples con formato:")
        print("   origen,destino,distancia")
        print("\n   Para archivos GDELT (20251004.export.CSV), usa la opción 3")
        
        print("\nArchivos disponibles en la carpeta 'data/':")
        if os.path.exists('data'):
            # Excluir archivos GDELT (que contienen 'export' o '20251004')
            files = [f for f in os.listdir('data') 
                    if f.endswith('.csv') 
                    and not 'export' in f.lower() 
                    and not '20251004' in f
                    and not f.startswith('202')]
            if files:
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {file}")
                print(f"\n  ⚠️  Archivos GDELT (20251004.csv, etc.) no se muestran aquí.")
                print(f"      Usa la opción 3 para cargar archivos GDELT.")
            else:
                print("  No hay archivos CSV simples disponibles.")
        
        filepath = input("\nIngrese la ruta del archivo CSV (o nombre si está en 'data/'): ").strip()
        
        if not filepath:
            print("❌ Ruta vacía. Operación cancelada.")
            return
        
        # Si no tiene ruta completa, buscar en data/
        if not os.path.isabs(filepath) and not os.path.exists(filepath):
            filepath = os.path.join('data', filepath)
        
        if not os.path.exists(filepath):
            print(f"❌ El archivo '{filepath}' no existe.")
            return
        
        try:
            print("\n⏳ Cargando dataset...")
            start_time = time.time()
            
            self.graph = Graph()
            edges_loaded = self.graph.load_from_csv(filepath)
            
            elapsed_time = time.time() - start_time
            
            self.dataset_loaded = True
            stats = self.graph.get_stats()
            
            print(f"\n✓ Dataset cargado exitosamente!")
            print(f"  • Nodos: {stats['num_nodes']}")
            print(f"  • Aristas: {stats['num_edges']}")
            print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
            print(f"  • Tiempo de carga: {elapsed_time:.3f} segundos")
            
        except Exception as e:
            print(f"❌ Error al cargar el dataset: {str(e)}")
            self.dataset_loaded = False
    
    def load_json_dataset(self):
        """Carga un dataset desde un archivo JSON."""
        print("\n" + "─" * 70)
        print("CARGAR DATASET JSON")
        print("─" * 70)
        
        print("\nArchivos disponibles en la carpeta 'data/':")
        if os.path.exists('data'):
            files = [f for f in os.listdir('data') if f.endswith('.json')]
            if files:
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {file}")
            else:
                print("  No hay archivos JSON disponibles.")
        
        filepath = input("\nIngrese la ruta del archivo JSON (o nombre si está en 'data/'): ").strip()
        
        if not filepath:
            print("❌ Ruta vacía. Operación cancelada.")
            return
        
        if not os.path.isabs(filepath) and not os.path.exists(filepath):
            filepath = os.path.join('data', filepath)
        
        if not os.path.exists(filepath):
            print(f"❌ El archivo '{filepath}' no existe.")
            return
        
        try:
            print("\n⏳ Cargando dataset...")
            start_time = time.time()
            
            self.graph = Graph()
            edges_loaded = self.graph.load_from_json(filepath)
            
            elapsed_time = time.time() - start_time
            
            self.dataset_loaded = True
            stats = self.graph.get_stats()
            
            print(f"\n✓ Dataset cargado exitosamente!")
            print(f"  • Nodos: {stats['num_nodes']}")
            print(f"  • Aristas: {stats['num_edges']}")
            print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
            print(f"  • Tiempo de carga: {elapsed_time:.3f} segundos")
            
        except Exception as e:
            print(f"❌ Error al cargar el dataset: {str(e)}")
            self.dataset_loaded = False
    
    def load_gdelt_dataset(self):
        """Carga un dataset GDELT."""
        print("\n" + "─" * 70)
        print("CARGAR DATASET GDELT")
        print("─" * 70)
        
        print("\nArchivos GDELT disponibles en la carpeta 'data/':")
        if os.path.exists('data'):
            # Mostrar archivos que parecen ser GDELT
            all_files = [f for f in os.listdir('data') if f.endswith('.CSV') or f.endswith('.csv')]
            gdelt_files = [f for f in all_files if '20251004' in f or 'export' in f.lower() or f.startswith('202')]
            other_files = [f for f in all_files if f not in gdelt_files]
            
            if gdelt_files:
                print("\n  Archivos GDELT detectados:")
                for i, file in enumerate(gdelt_files, 1):
                    print(f"    {i}. {file} ⭐")
            
            if other_files and len(other_files) <= 5:
                print("\n  Otros archivos CSV (probablemente no GDELT):")
                for i, file in enumerate(other_files, 1):
                    print(f"    {i}. {file}")
            
            if not gdelt_files and not other_files:
                print("  No hay archivos CSV disponibles.")
        
        filepath = input("\nIngrese la ruta del archivo GDELT (o nombre si está en 'data/'): ").strip()
        
        if not filepath:
            print("❌ Ruta vacía. Operación cancelada.")
            return
        
        if not os.path.isabs(filepath) and not os.path.exists(filepath):
            filepath = os.path.join('data', filepath)
        
        if not os.path.exists(filepath):
            print(f"❌ El archivo '{filepath}' no existe.")
            return
        
        # Opciones de filtrado
        print("\n¿Desea filtrar por país?")
        country_filter = input("Código de país (ej: USA, CAN) o Enter para todos: ").strip().upper()
        if not country_filter:
            country_filter = None
        
        print("\n¿Cuántos eventos desea cargar?")
        max_rows_input = input("Número de eventos (Enter para 1000): ").strip()
        max_rows = int(max_rows_input) if max_rows_input else 1000
        
        print("\nDistancia máxima para conectar eventos (km):")
        max_dist_input = input("Distancia (Enter para 500 km): ").strip()
        max_distance = float(max_dist_input) if max_dist_input else 500.0
        
        try:
            print("\n⏳ Cargando dataset GDELT...")
            print("   (Esto puede tardar varios segundos...)")
            start_time = time.time()
            
            self.graph = Graph()
            edges_loaded = self.graph.load_from_gdelt(
                filepath=filepath,
                country_filter=country_filter,
                max_rows=max_rows,
                max_distance=max_distance
            )
            
            elapsed_time = time.time() - start_time
            
            self.dataset_loaded = True
            stats = self.graph.get_stats()
            
            print(f"\n✓ Dataset GDELT cargado exitosamente!")
            print(f"  • Eventos (nodos): {stats['num_nodes']}")
            print(f"  • Conexiones (aristas): {stats['num_edges']}")
            print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
            if country_filter:
                print(f"  • Filtrado por país: {country_filter}")
            print(f"  • Tiempo de carga: {elapsed_time:.3f} segundos")
            
        except Exception as e:
            print(f"❌ Error al cargar el dataset GDELT: {str(e)}")
            self.dataset_loaded = False
    
    def search_nodes_interactive(self):
        """Búsqueda interactiva de nodos."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("BÚSQUEDA DE NODOS")
        print("─" * 70)
        
        print("\nOpciones de búsqueda:")
        print("  1. Buscar por texto (ID, nombre, ubicación)")
        print("  2. Filtrar por código de país")
        print("  3. Ver detalles de un nodo específico")
        
        option = input("\nSeleccione una opción: ").strip()
        
        if option == '1':
            query = input("\nIngrese texto a buscar: ").strip()
            if not query:
                print("❌ Búsqueda vacía.")
                return
            
            print("\n⏳ Buscando...")
            results = self.graph.search_nodes(query, limit=50)
            
            if not results:
                print(f"\n❌ No se encontraron nodos que coincidan con '{query}'.")
            else:
                print(f"\n✓ Se encontraron {len(results)} nodos:")
                for i, node_id in enumerate(results[:20], 1):
                    node = self.graph.get_node(node_id)
                    print(f"  {i}. {node_id} - {node.name}")
                
                if len(results) > 20:
                    print(f"\n  ... y {len(results) - 20} resultados más")
        
        elif option == '2':
            country_code = input("\nIngrese código de país (ej: USA, CAN): ").strip().upper()
            if not country_code:
                print("❌ Código vacío.")
                return
            
            print("\n⏳ Filtrando...")
            results = self.graph.filter_nodes_by_country(country_code)
            
            if not results:
                print(f"\n❌ No se encontraron nodos del país '{country_code}'.")
            else:
                print(f"\n✓ Se encontraron {len(results)} nodos de {country_code}:")
                for i, node_id in enumerate(results[:20], 1):
                    node = self.graph.get_node(node_id)
                    print(f"  {i}. {node_id} - {node.name}")
                
                if len(results) > 20:
                    print(f"\n  ... y {len(results) - 20} resultados más")
        
        elif option == '3':
            node_id = input("\nIngrese el ID del nodo: ").strip()
            if not self.graph.node_exists(node_id):
                print(f"\n❌ El nodo '{node_id}' no existe.")
                return
            
            node = self.graph.get_node(node_id)
            metadata = self.graph.get_node_metadata(node_id)
            
            print(f"\n" + "─" * 70)
            print(f"DETALLES DEL NODO: {node_id}")
            print("─" * 70)
            print(f"\n  Nombre: {node.name}")
            print(f"  Coordenadas: ({node.y:.4f}, {node.x:.4f})")
            
            if metadata:
                print(f"\n  Metadata:")
                for key, value in metadata.items():
                    if value:
                        print(f"    • {key}: {value}")
            
            neighbors = self.graph.get_neighbors(node_id)
            print(f"\n  Conexiones: {len(neighbors)} nodos")
            if neighbors:
                print(f"\n  Primeros 5 vecinos:")
                for neighbor_id, weight in neighbors[:5]:
                    print(f"    → {neighbor_id} (distancia: {weight:.2f} km)")
        
        else:
            print("\n❌ Opción inválida.")
    
    def generate_random_dataset(self):
        """Genera un dataset aleatorio."""
        print("\n" + "─" * 70)
        print("GENERAR DATASET ALEATORIO")
        print("─" * 70)
        
        print("\nTipos de grafos disponibles:")
        print("  1. Cuadrícula (estructura de calles)")
        print("  2. Clusters (barrios conectados)")
        print("  3. Aleatorio (conexiones por proximidad)")
        
        graph_type = input("\nSeleccione el tipo de grafo (1-3): ").strip()
        
        try:
            num_nodes = int(input("Ingrese el número de nodos (recomendado: 1500): ").strip())
            if num_nodes < 10:
                print("❌ El número de nodos debe ser al menos 10.")
                return
        except ValueError:
            print("❌ Número inválido.")
            return
        
        print("\n⏳ Generando dataset...")
        start_time = time.time()
        
        try:
            from data.dataset_generator import CityGraphGenerator
            
            generator = CityGraphGenerator(num_nodes=num_nodes)
            
            if graph_type == '1':
                edges = generator.generate_grid_based_city()
            elif graph_type == '2':
                edges = generator.generate_clustered_city()
            elif graph_type == '3':
                edges = generator.generate_random_city()
            else:
                print("❌ Opción inválida.")
                return
            
            self.graph = Graph()
            for source, destination, weight in edges:
                self.graph.add_edge(source, destination, weight)
            
            elapsed_time = time.time() - start_time
            
            self.dataset_loaded = True
            stats = self.graph.get_stats()
            
            print(f"\n✓ Dataset generado exitosamente!")
            print(f"  • Nodos: {stats['num_nodes']}")
            print(f"  • Aristas: {stats['num_edges']}")
            print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
            print(f"  • Tiempo de generación: {elapsed_time:.3f} segundos")
            
            # Preguntar si desea guardar
            save = input("\n¿Desea guardar este dataset? (s/n): ").strip().lower()
            if save == 's':
                filename = input("Ingrese el nombre del archivo (sin extensión): ").strip()
                if filename:
                    filepath = os.path.join('data', f"{filename}.csv")
                    os.makedirs('data', exist_ok=True)
                    self.graph.save_to_csv(filepath)
                    print(f"✓ Dataset guardado en '{filepath}'")
            
        except Exception as e:
            print(f"❌ Error al generar el dataset: {str(e)}")
            self.dataset_loaded = False
    
    def find_route_dijkstra(self):
        """Busca la ruta más corta usando Dijkstra."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("BÚSQUEDA DE RUTA - ALGORITMO DE DIJKSTRA")
        print("─" * 70)
        
        start_node = input("\nIngrese el nodo inicial: ").strip()
        end_node = input("Ingrese el nodo final: ").strip()
        
        if not start_node or not end_node:
            print("❌ Debe ingresar ambos nodos.")
            return
        
        if not self.graph.node_exists(start_node):
            print(f"❌ El nodo '{start_node}' no existe en el grafo.")
            return
        
        if not self.graph.node_exists(end_node):
            print(f"❌ El nodo '{end_node}' no existe en el grafo.")
            return
        
        try:
            print("\n⏳ Calculando ruta más corta...")
            start_time = time.time()
            
            distance, path = dijkstra(self.graph, start_node, end_node)
            
            elapsed_time = time.time() - start_time
            
            if distance is None:
                print(f"\n❌ No existe un camino entre '{start_node}' y '{end_node}'.")
                self.last_path = None
            else:
                self.last_path = path  # Guardar para visualización
                print(f"\n✓ Ruta encontrada!")
                print(f"\n  Origen: {start_node}")
                print(f"  Destino: {end_node}")
                print(f"  Distancia total: {distance:.2f} unidades")
                print(f"  Número de nodos en la ruta: {len(path)}")
                print(f"  Tiempo de ejecución: {elapsed_time*1000:.2f} ms")
                print(f"\n  Ruta completa:")
                print(f"  {' → '.join(path)}")
                
                # Mostrar detalles de cada segmento
                if len(path) > 1:
                    print(f"\n  Detalles por segmento:")
                    for i in range(len(path) - 1):
                        segment_weight = self.graph.get_edge_weight(path[i], path[i+1])
                        print(f"    {path[i]} → {path[i+1]}: {segment_weight:.2f} unidades")
            
        except Exception as e:
            print(f"❌ Error al calcular la ruta: {str(e)}")
    
    def find_route_bellman_ford(self):
        """Busca la ruta más corta usando Bellman-Ford."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("BÚSQUEDA DE RUTA - ALGORITMO DE BELLMAN-FORD")
        print("─" * 70)
        
        start_node = input("\nIngrese el nodo inicial: ").strip()
        end_node = input("Ingrese el nodo final: ").strip()
        
        if not start_node or not end_node:
            print("❌ Debe ingresar ambos nodos.")
            return
        
        if not self.graph.node_exists(start_node):
            print(f"❌ El nodo '{start_node}' no existe en el grafo.")
            return
        
        if not self.graph.node_exists(end_node):
            print(f"❌ El nodo '{end_node}' no existe en el grafo.")
            return
        
        try:
            print("\n⏳ Calculando ruta más corta...")
            start_time = time.time()
            
            distance, path, has_negative_cycle = bellman_ford(self.graph, start_node, end_node)
            
            elapsed_time = time.time() - start_time
            
            if has_negative_cycle:
                print(f"\n⚠️  Se detectó un ciclo negativo en el grafo.")
                print("    No se puede calcular la ruta más corta.")
                self.last_path = None
            elif distance is None:
                print(f"\n❌ No existe un camino entre '{start_node}' y '{end_node}'.")
                self.last_path = None
            else:
                self.last_path = path  # Guardar para visualización
                print(f"\n✓ Ruta encontrada!")
                print(f"\n  Origen: {start_node}")
                print(f"  Destino: {end_node}")
                print(f"  Distancia total: {distance:.2f} unidades")
                print(f"  Número de nodos en la ruta: {len(path)}")
                print(f"  Tiempo de ejecución: {elapsed_time*1000:.2f} ms")
                print(f"\n  Ruta completa:")
                print(f"  {' → '.join(path)}")
            
        except Exception as e:
            print(f"❌ Error al calcular la ruta: {str(e)}")
    
    def calculate_all_routes(self):
        """Calcula todas las rutas usando Floyd-Warshall."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        stats = self.graph.get_stats()
        if stats['num_nodes'] > 500:
            print(f"\n⚠️  Advertencia: El grafo tiene {stats['num_nodes']} nodos.")
            print("   Floyd-Warshall puede tardar mucho tiempo con grafos grandes.")
            confirm = input("   ¿Desea continuar? (s/n): ").strip().lower()
            if confirm != 's':
                return
        
        print("\n" + "─" * 70)
        print("CALCULAR TODAS LAS RUTAS - ALGORITMO DE FLOYD-WARSHALL")
        print("─" * 70)
        
        try:
            print("\n⏳ Calculando todas las rutas más cortas...")
            print("   (Esto puede tardar varios segundos...)")
            start_time = time.time()
            
            distances, next_nodes = floyd_warshall(self.graph)
            
            elapsed_time = time.time() - start_time
            
            print(f"\n✓ Cálculo completado!")
            print(f"  Tiempo de ejecución: {elapsed_time:.2f} segundos")
            
            # Permitir consultas
            while True:
                print("\n" + "─" * 70)
                start_node = input("Ingrese el nodo inicial (o 'q' para salir): ").strip()
                if start_node.lower() == 'q':
                    break
                
                end_node = input("Ingrese el nodo final: ").strip()
                
                if not self.graph.node_exists(start_node) or not self.graph.node_exists(end_node):
                    print("❌ Uno o ambos nodos no existen.")
                    continue
                
                distance = distances.get((start_node, end_node))
                if distance == float('infinity'):
                    print(f"\n❌ No existe un camino entre '{start_node}' y '{end_node}'.")
                else:
                    path = get_path_floyd_warshall(next_nodes, start_node, end_node)
                    print(f"\n✓ Ruta encontrada!")
                    print(f"  Distancia total: {distance:.2f} unidades")
                    print(f"  Ruta: {' → '.join(path)}")
            
        except Exception as e:
            print(f"❌ Error al calcular las rutas: {str(e)}")
    
    def show_statistics(self):
        """Muestra estadísticas del grafo cargado."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("ESTADÍSTICAS DEL GRAFO")
        print("─" * 70)
        
        stats = self.graph.get_stats()
        
        print(f"\n  Número de nodos: {stats['num_nodes']}")
        print(f"  Número de aristas: {stats['num_edges']}")
        print(f"  Grado promedio: {stats['avg_degree']:.2f}")
        print(f"  Densidad del grafo: {stats['num_edges'] / (stats['num_nodes'] * (stats['num_nodes'] - 1)):.4f}")
    
    def list_sample_nodes(self):
        """Lista algunos nodos disponibles."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("NODOS DISPONIBLES (MUESTRA)")
        print("─" * 70)
        
        all_nodes = self.graph.get_all_nodes()
        sample_size = min(50, len(all_nodes))
        
        print(f"\nMostrando {sample_size} de {len(all_nodes)} nodos:")
        print()
        
        for i in range(0, sample_size, 5):
            row = all_nodes[i:i+5]
            print("  " + "  ".join(f"{node:15}" for node in row))
        
        if len(all_nodes) > sample_size:
            print(f"\n  ... y {len(all_nodes) - sample_size} nodos más")
    
    def run_performance_tests(self):
        """Ejecuta pruebas de rendimiento."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("PRUEBAS DE RENDIMIENTO")
        print("─" * 70)
        
        all_nodes = self.graph.get_all_nodes()
        if len(all_nodes) < 2:
            print("\n❌ El grafo debe tener al menos 2 nodos.")
            return
        
        # Seleccionar nodos aleatorios para las pruebas
        import random
        test_pairs = [(random.choice(all_nodes), random.choice(all_nodes)) for _ in range(5)]
        
        print("\nEjecutando 5 búsquedas con Dijkstra...")
        dijkstra_times = []
        
        for i, (start, end) in enumerate(test_pairs, 1):
            start_time = time.time()
            distance, path = dijkstra(self.graph, start, end)
            elapsed = time.time() - start_time
            dijkstra_times.append(elapsed)
            
            status = "✓" if distance is not None else "✗"
            print(f"  {status} Prueba {i}: {start} → {end} - {elapsed*1000:.2f} ms")
        
        avg_dijkstra = sum(dijkstra_times) / len(dijkstra_times)
        
        print(f"\n  Tiempo promedio (Dijkstra): {avg_dijkstra*1000:.2f} ms")
        print(f"  Tiempo mínimo: {min(dijkstra_times)*1000:.2f} ms")
        print(f"  Tiempo máximo: {max(dijkstra_times)*1000:.2f} ms")
    
    def visualize_graph(self):
        """Visualiza el grafo usando Graphviz."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        print("\n" + "─" * 70)
        print("VISUALIZAR GRAFO CON GRAPHVIZ")
        print("─" * 70)
        
        try:
            from visualization.graph_visualizer import GraphVisualizer
            
            visualizer = GraphVisualizer(self.graph)
            
            if not visualizer.graphviz_available:
                print("\n⚠️  Graphviz no está instalado.")
                print("\nPara instalar Graphviz:")
                print("  1. Instala la librería Python: pip install graphviz")
                print("  2. Descarga e instala Graphviz: https://graphviz.org/download/")
                print("  3. Durante la instalación, selecciona 'Add Graphviz to system PATH'")
                print("  4. Reinicia tu terminal/IDE")
                return
            
            stats = self.graph.get_stats()
            
            print(f"\nEl grafo tiene {stats['num_nodes']} nodos.")
            
            if stats['num_nodes'] > 100:
                print("⚠️  Grafos grandes pueden tardar en renderizarse.")
                max_nodes = input("¿Cuántos nodos desea visualizar? (max recomendado: 100): ").strip()
                try:
                    max_nodes = int(max_nodes)
                except:
                    max_nodes = 100
            else:
                max_nodes = stats['num_nodes']
            
            output_file = input("\nNombre del archivo de salida (sin extensión, default: 'grafo'): ").strip()
            if not output_file:
                output_file = 'grafo'
            
            print("\nFormatos disponibles: png, pdf, svg")
            format_choice = input("Formato (default: png): ").strip().lower()
            if format_choice not in ['png', 'pdf', 'svg']:
                format_choice = 'png'
            
            print("\nMotores disponibles:")
            print("  dot - Jerárquico (recomendado)")
            print("  neato - Fuerza dirigida")
            print("  fdp - Fuerza dirigida (grafos grandes)")
            print("  circo - Circular")
            engine = input("Motor (default: dot): ").strip().lower()
            if engine not in ['dot', 'neato', 'fdp', 'circo', 'twopi']:
                engine = 'dot'
            
            print("\n⏳ Generando visualización...")
            success = visualizer.visualize_graph(
                output_file=output_file,
                format=format_choice,
                max_nodes=max_nodes,
                engine=engine
            )
            
            if success:
                print(f"\n✓ Archivo generado: {output_file}.{format_choice}")
                print("  Puedes abrirlo con cualquier visor de imágenes.")
            
        except ImportError:
            print("\n❌ Módulo de visualización no disponible.")
            print("   Instala graphviz: pip install graphviz")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    def visualize_last_path(self):
        """Visualiza la última ruta encontrada."""
        if not self.dataset_loaded or self.graph is None:
            print("\n❌ Primero debe cargar un dataset.")
            return
        
        if self.last_path is None:
            print("\n❌ No hay ninguna ruta para visualizar.")
            print("   Primero busca una ruta con las opciones 4, 5 o 6.")
            return
        
        print("\n" + "─" * 70)
        print("VISUALIZAR RUTA CON GRAPHVIZ")
        print("─" * 70)
        
        try:
            from visualization.graph_visualizer import GraphVisualizer
            
            visualizer = GraphVisualizer(self.graph)
            
            if not visualizer.graphviz_available:
                print("\n⚠️  Graphviz no está instalado.")
                print("\nPara instalar Graphviz:")
                print("  1. Instala la librería Python: pip install graphviz")
                print("  2. Descarga e instala Graphviz: https://graphviz.org/download/")
                print("  3. Durante la instalación, selecciona 'Add Graphviz to system PATH'")
                print("  4. Reinicia tu terminal/IDE")
                return
            
            print(f"\nRuta a visualizar: {len(self.last_path)} nodos")
            print(f"  Inicio: {self.last_path[0]}")
            print(f"  Fin: {self.last_path[-1]}")
            
            output_file = input("\nNombre del archivo de salida (sin extensión, default: 'ruta'): ").strip()
            if not output_file:
                output_file = 'ruta'
            
            print("\nFormatos disponibles: png, pdf, svg")
            format_choice = input("Formato (default: png): ").strip().lower()
            if format_choice not in ['png', 'pdf', 'svg']:
                format_choice = 'png'
            
            show_context = input("\n¿Mostrar nodos vecinos para contexto? (s/n, default: s): ").strip().lower()
            show_context = show_context != 'n'
            
            print("\n⏳ Generando visualización de la ruta...")
            success = visualizer.visualize_path(
                path=self.last_path,
                output_file=output_file,
                format=format_choice,
                show_context=show_context
            )
            
            if success:
                print(f"\n✓ Archivo generado: {output_file}.{format_choice}")
                print("  Puedes abrirlo con cualquier visor de imágenes.")
                print("\n  Leyenda:")
                print("    🟢 Verde = Nodo inicial")
                print("    🔴 Rojo = Nodo final")
                print("    🟡 Amarillo = Nodos intermedios")
                print("    ⚪ Gris = Nodos de contexto")
            
        except ImportError:
            print("\n❌ Módulo de visualización no disponible.")
            print("   Instala graphviz: pip install graphviz")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    def run(self):
        """Ejecuta la aplicación principal."""
        while True:
            self.clear_screen()
            self.print_header()
            
            if self.dataset_loaded:
                stats = self.graph.get_stats()
                print(f"📊 Dataset cargado: {stats['num_nodes']} nodos, {stats['num_edges']} aristas")
            else:
                print("⚠️  No hay dataset cargado")
            
            self.print_menu()
            
            choice = input("\nSeleccione una opción: ").strip()
            
            if choice == '1':
                self.load_csv_dataset()
            elif choice == '2':
                self.load_json_dataset()
            elif choice == '3':
                self.load_gdelt_dataset()
            elif choice == '4':
                self.generate_random_dataset()
            elif choice == '5':
                self.search_nodes_interactive()
            elif choice == '6':
                self.find_route_dijkstra()
            elif choice == '7':
                self.find_route_bellman_ford()
            elif choice == '8':
                self.calculate_all_routes()
            elif choice == '9':
                self.show_statistics()
            elif choice == '10':
                self.list_sample_nodes()
            elif choice == '11':
                self.run_performance_tests()
            elif choice == '12':
                self.visualize_graph()
            elif choice == '13':
                self.visualize_last_path()
            elif choice == '0':
                print("\n¡Gracias por usar el Sistema de Rutas Óptimas!")
                print("Hasta luego.\n")
                break
            else:
                print("\n❌ Opción inválida. Intente nuevamente.")
            
            if choice != '0':
                input("\nPresione Enter para continuar...")


def main():
    """Función principal."""
    app = RouteFinderApp()
    app.run()


if __name__ == '__main__':
    main()
