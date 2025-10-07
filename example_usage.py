"""
Ejemplos de uso del sistema de rutas óptimas.
Demuestra cómo usar las diferentes funcionalidades programáticamente.
"""

import time
from models.graph import Graph
from algorithms.dijkstra import dijkstra, dijkstra_all_paths
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, get_path_floyd_warshall
from data.dataset_generator import CityGraphGenerator


def ejemplo_1_grafo_simple():
    """Ejemplo 1: Crear un grafo simple y buscar ruta con Dijkstra."""
    print("=" * 70)
    print("EJEMPLO 1: Grafo Simple con Dijkstra")
    print("=" * 70)
    
    # Crear grafo
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 3)
    graph.add_edge('B', 'D', 2)
    graph.add_edge('C', 'D', 6)
    graph.add_edge('C', 'B', 1)
    
    print("\nGrafo creado:")
    print("  A → B (5)")
    print("  A → C (3)")
    print("  B → D (2)")
    print("  C → D (6)")
    print("  C → B (1)")
    
    # Buscar ruta
    print("\nBuscando ruta de A a D con Dijkstra...")
    distance, path = dijkstra(graph, 'A', 'D')
    
    print(f"\n✓ Ruta encontrada:")
    print(f"  Distancia: {distance}")
    print(f"  Camino: {' → '.join(path)}")
    print()


def ejemplo_2_cargar_csv():
    """Ejemplo 2: Cargar grafo desde CSV y buscar ruta."""
    print("=" * 70)
    print("EJEMPLO 2: Cargar desde CSV")
    print("=" * 70)
    
    # Crear un CSV de ejemplo
    import csv
    filename = 'data/ejemplo_ciudad.csv'
    
    edges = [
        ('Inicio', 'PlazaMayor', 10),
        ('Inicio', 'Parque', 15),
        ('PlazaMayor', 'Hospital', 8),
        ('Parque', 'Hospital', 12),
        ('Hospital', 'Universidad', 5),
        ('PlazaMayor', 'Universidad', 20),
        ('Universidad', 'Destino', 7),
        ('Hospital', 'Destino', 15)
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origen', 'destino', 'distancia'])
        for src, dst, dist in edges:
            writer.writerow([src, dst, dist])
    
    print(f"\n✓ Archivo CSV creado: {filename}")
    
    # Cargar grafo
    graph = Graph()
    graph.load_from_csv(filename)
    
    stats = graph.get_stats()
    print(f"\n✓ Grafo cargado:")
    print(f"  Nodos: {stats['num_nodes']}")
    print(f"  Aristas: {stats['num_edges']}")
    
    # Buscar ruta
    print("\nBuscando ruta de 'Inicio' a 'Destino'...")
    distance, path = dijkstra(graph, 'Inicio', 'Destino')
    
    print(f"\n✓ Ruta encontrada:")
    print(f"  Distancia: {distance} km")
    print(f"  Camino: {' → '.join(path)}")
    print()


def ejemplo_3_comparar_algoritmos():
    """Ejemplo 3: Comparar rendimiento de Dijkstra vs Bellman-Ford."""
    print("=" * 70)
    print("EJEMPLO 3: Comparación de Algoritmos")
    print("=" * 70)
    
    # Generar grafo mediano
    print("\nGenerando grafo de 200 nodos...")
    generator = CityGraphGenerator(num_nodes=200, seed=42)
    edges = generator.generate_grid_based_city()
    
    graph = Graph()
    for src, dst, weight in edges:
        graph.add_edge(src, dst, weight)
    
    stats = graph.get_stats()
    print(f"✓ Grafo generado: {stats['num_nodes']} nodos, {stats['num_edges']} aristas")
    
    # Seleccionar nodos
    start = 'N0_0'
    end = 'N13_13'
    
    # Dijkstra
    print(f"\n1. Ejecutando Dijkstra ({start} → {end})...")
    start_time = time.time()
    dist_d, path_d = dijkstra(graph, start, end)
    time_d = time.time() - start_time
    
    print(f"   Distancia: {dist_d:.2f}")
    print(f"   Nodos en ruta: {len(path_d)}")
    print(f"   Tiempo: {time_d*1000:.2f} ms")
    
    # Bellman-Ford
    print(f"\n2. Ejecutando Bellman-Ford ({start} → {end})...")
    start_time = time.time()
    dist_b, path_b, _ = bellman_ford(graph, start, end)
    time_b = time.time() - start_time
    
    print(f"   Distancia: {dist_b:.2f}")
    print(f"   Nodos en ruta: {len(path_b)}")
    print(f"   Tiempo: {time_b*1000:.2f} ms")
    
    # Comparación
    print(f"\n📊 Comparación:")
    print(f"   Dijkstra es {time_b/time_d:.1f}x más rápido que Bellman-Ford")
    print(f"   Ambos encontraron la misma distancia: {dist_d == dist_b}")
    print()


def ejemplo_4_generar_dataset_grande():
    """Ejemplo 4: Generar y analizar dataset grande."""
    print("=" * 70)
    print("EJEMPLO 4: Dataset Grande (1500 nodos)")
    print("=" * 70)
    
    print("\nGenerando grafo con estructura de clusters...")
    start_time = time.time()
    
    generator = CityGraphGenerator(num_nodes=1500, seed=42)
    edges = generator.generate_clustered_city(num_clusters=15)
    
    graph = Graph()
    for src, dst, weight in edges:
        graph.add_edge(src, dst, weight)
    
    gen_time = time.time() - start_time
    
    stats = graph.get_stats()
    print(f"\n✓ Grafo generado en {gen_time:.2f} segundos")
    print(f"  Nodos: {stats['num_nodes']}")
    print(f"  Aristas: {stats['num_edges']}")
    print(f"  Grado promedio: {stats['avg_degree']:.2f}")
    
    # Guardar
    filename = 'data/ejemplo_grande_1500.csv'
    graph.save_to_csv(filename)
    print(f"\n✓ Guardado en: {filename}")
    
    # Probar búsqueda
    print("\nProbando búsqueda en grafo grande...")
    start_time = time.time()
    distance, path = dijkstra(graph, 'C0_N0', 'C14_N49')
    search_time = time.time() - start_time
    
    if distance:
        print(f"\n✓ Ruta encontrada:")
        print(f"  Distancia: {distance:.2f}")
        print(f"  Nodos en ruta: {len(path)}")
        print(f"  Tiempo de búsqueda: {search_time*1000:.2f} ms")
        print(f"  Primeros 5 nodos: {' → '.join(path[:5])} ...")
        print(f"  Últimos 5 nodos: ... {' → '.join(path[-5:])}")
    else:
        print("  No se encontró ruta entre esos nodos")
    print()


def ejemplo_5_floyd_warshall():
    """Ejemplo 5: Usar Floyd-Warshall para múltiples consultas."""
    print("=" * 70)
    print("EJEMPLO 5: Floyd-Warshall - Múltiples Consultas")
    print("=" * 70)
    
    # Crear grafo pequeño
    print("\nCreando grafo de 50 nodos...")
    generator = CityGraphGenerator(num_nodes=50, seed=42)
    edges = generator.generate_grid_based_city()
    
    graph = Graph()
    for src, dst, weight in edges:
        graph.add_edge(src, dst, weight)
    
    print("✓ Grafo creado")
    
    # Calcular todas las rutas
    print("\nCalculando todas las rutas con Floyd-Warshall...")
    start_time = time.time()
    distances, next_nodes = floyd_warshall(graph)
    fw_time = time.time() - start_time
    
    print(f"✓ Cálculo completado en {fw_time:.2f} segundos")
    
    # Hacer múltiples consultas
    print("\nConsultando 5 rutas diferentes:")
    queries = [
        ('N0_0', 'N5_5'),
        ('N1_1', 'N6_6'),
        ('N2_2', 'N4_4'),
        ('N0_0', 'N7_0'),
        ('N3_3', 'N6_3')
    ]
    
    total_query_time = 0
    for i, (start, end) in enumerate(queries, 1):
        start_time = time.time()
        dist = distances.get((start, end), float('infinity'))
        path = get_path_floyd_warshall(next_nodes, start, end)
        query_time = time.time() - start_time
        total_query_time += query_time
        
        if dist != float('infinity') and path:
            print(f"\n  {i}. {start} → {end}")
            print(f"     Distancia: {dist:.2f}")
            print(f"     Nodos: {len(path)}")
            print(f"     Tiempo: {query_time*1000:.4f} ms")
    
    print(f"\n📊 Resumen:")
    print(f"   Tiempo de precálculo: {fw_time:.2f} s")
    print(f"   Tiempo promedio por consulta: {(total_query_time/5)*1000:.4f} ms")
    print(f"   Las consultas son extremadamente rápidas después del precálculo")
    print()


def ejemplo_6_estadisticas():
    """Ejemplo 6: Análisis estadístico de diferentes tipos de grafos."""
    print("=" * 70)
    print("EJEMPLO 6: Análisis Estadístico de Grafos")
    print("=" * 70)
    
    generator = CityGraphGenerator(num_nodes=500, seed=42)
    
    graph_types = [
        ('Cuadrícula', generator.generate_grid_based_city()),
        ('Clusters', generator.generate_clustered_city(num_clusters=10)),
        ('Aleatorio', generator.generate_random_city(avg_connections=4))
    ]
    
    print("\nComparando 3 tipos de grafos (500 nodos cada uno):\n")
    
    for name, edges in graph_types:
        graph = Graph()
        for src, dst, weight in edges:
            graph.add_edge(src, dst, weight)
        
        stats = graph.get_stats()
        
        print(f"📊 {name}:")
        print(f"   Nodos: {stats['num_nodes']}")
        print(f"   Aristas: {stats['num_edges']}")
        print(f"   Grado promedio: {stats['avg_degree']:.2f}")
        print(f"   Densidad: {stats['num_edges']/(stats['num_nodes']*(stats['num_nodes']-1)):.4f}")
        
        # Probar búsqueda
        start_time = time.time()
        distance, path = dijkstra(graph, 'N0_0', 'N10_10' if 'N10_10' in graph.get_all_nodes() else graph.get_all_nodes()[100])
        search_time = time.time() - start_time
        
        if distance:
            print(f"   Búsqueda de ejemplo: {search_time*1000:.2f} ms")
        print()


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 70)
    print(" " * 20 + "EJEMPLOS DE USO")
    print(" " * 15 + "Sistema de Rutas Óptimas")
    print("=" * 70 + "\n")
    
    ejemplos = [
        ejemplo_1_grafo_simple,
        ejemplo_2_cargar_csv,
        ejemplo_3_comparar_algoritmos,
        ejemplo_4_generar_dataset_grande,
        ejemplo_5_floyd_warshall,
        ejemplo_6_estadisticas
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        try:
            ejemplo()
            if i < len(ejemplos):
                input("Presiona Enter para continuar al siguiente ejemplo...")
                print("\n")
        except Exception as e:
            print(f"❌ Error en ejemplo {i}: {str(e)}\n")
    
    print("=" * 70)
    print("¡Todos los ejemplos completados!")
    print("=" * 70)


if __name__ == '__main__':
    main()
