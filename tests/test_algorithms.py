"""
Pruebas unitarias para los algoritmos de búsqueda de rutas.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.graph import Graph
from algorithms.dijkstra import dijkstra
from algorithms.bellman_ford import bellman_ford
from algorithms.floyd_warshall import floyd_warshall, get_path_floyd_warshall


def test_dijkstra_simple():
    """Prueba básica del algoritmo de Dijkstra."""
    print("Test 1: Dijkstra - Grafo simple")
    
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 3)
    graph.add_edge('B', 'D', 2)
    graph.add_edge('C', 'D', 6)
    graph.add_edge('C', 'B', 1)
    
    distance, path = dijkstra(graph, 'A', 'D')
    
    assert distance == 6, f"Distancia esperada: 6, obtenida: {distance}"
    assert path == ['A', 'C', 'B', 'D'], f"Ruta esperada: ['A', 'C', 'B', 'D'], obtenida: {path}"
    
    print(f"  ✓ Distancia: {distance}")
    print(f"  ✓ Ruta: {' -> '.join(path)}")
    print("  ✓ Test pasado\n")


def test_dijkstra_no_path():
    """Prueba de Dijkstra cuando no existe camino."""
    print("Test 2: Dijkstra - Sin camino")
    
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('C', 'D', 3)
    
    distance, path = dijkstra(graph, 'A', 'D')
    
    assert distance is None, f"Distancia esperada: None, obtenida: {distance}"
    assert path is None, f"Ruta esperada: None, obtenida: {path}"
    
    print("  ✓ Correctamente detectado que no hay camino")
    print("  ✓ Test pasado\n")


def test_bellman_ford():
    """Prueba del algoritmo de Bellman-Ford."""
    print("Test 3: Bellman-Ford - Grafo simple")
    
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 3)
    graph.add_edge('B', 'D', 2)
    graph.add_edge('C', 'D', 6)
    graph.add_edge('C', 'B', 1)
    
    distance, path, has_negative_cycle = bellman_ford(graph, 'A', 'D')
    
    assert distance == 6, f"Distancia esperada: 6, obtenida: {distance}"
    assert path == ['A', 'C', 'B', 'D'], f"Ruta esperada: ['A', 'C', 'B', 'D'], obtenida: {path}"
    assert not has_negative_cycle, "No debería haber ciclo negativo"
    
    print(f"  ✓ Distancia: {distance}")
    print(f"  ✓ Ruta: {' -> '.join(path)}")
    print("  ✓ Test pasado\n")


def test_floyd_warshall():
    """Prueba del algoritmo de Floyd-Warshall."""
    print("Test 4: Floyd-Warshall - Todos los caminos")
    
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 3)
    graph.add_edge('B', 'D', 2)
    graph.add_edge('C', 'D', 6)
    graph.add_edge('C', 'B', 1)
    
    distances, next_nodes = floyd_warshall(graph)
    
    # Verificar distancia A -> D
    dist_ad = distances[('A', 'D')]
    assert dist_ad == 6, f"Distancia A->D esperada: 6, obtenida: {dist_ad}"
    
    # Verificar camino A -> D
    path = get_path_floyd_warshall(next_nodes, 'A', 'D')
    assert path == ['A', 'C', 'B', 'D'], f"Ruta esperada: ['A', 'C', 'B', 'D'], obtenida: {path}"
    
    print(f"  ✓ Distancia A->D: {dist_ad}")
    print(f"  ✓ Ruta A->D: {' -> '.join(path)}")
    print("  ✓ Test pasado\n")


def test_graph_operations():
    """Prueba operaciones básicas del grafo."""
    print("Test 5: Operaciones del grafo")
    
    graph = Graph()
    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 3)
    
    assert graph.node_exists('A'), "El nodo A debería existir"
    assert graph.node_exists('B'), "El nodo B debería existir"
    assert not graph.node_exists('Z'), "El nodo Z no debería existir"
    
    neighbors = graph.get_neighbors('A')
    assert len(neighbors) == 2, f"A debería tener 2 vecinos, tiene {len(neighbors)}"
    
    weight = graph.get_edge_weight('A', 'B')
    assert weight == 5, f"Peso A->B esperado: 5, obtenido: {weight}"
    
    stats = graph.get_stats()
    assert stats['num_nodes'] == 3, f"Número de nodos esperado: 3, obtenido: {stats['num_nodes']}"
    assert stats['num_edges'] == 2, f"Número de aristas esperado: 2, obtenido: {stats['num_edges']}"
    
    print("  ✓ Todas las operaciones del grafo funcionan correctamente")
    print("  ✓ Test pasado\n")


def test_large_graph_performance():
    """Prueba de rendimiento con un grafo más grande."""
    print("Test 6: Rendimiento con grafo grande (100 nodos)")
    
    import time
    
    graph = Graph()
    
    # Crear un grafo de 100 nodos en forma de cadena
    for i in range(100):
        for j in range(i + 1, min(i + 5, 100)):
            graph.add_edge(f'N{i}', f'N{j}', j - i)
    
    start_time = time.time()
    distance, path = dijkstra(graph, 'N0', 'N99')
    elapsed_time = time.time() - start_time
    
    assert distance is not None, "Debería existir un camino"
    assert path[0] == 'N0' and path[-1] == 'N99', "El camino debería ir de N0 a N99"
    
    print(f"  ✓ Distancia: {distance}")
    print(f"  ✓ Longitud del camino: {len(path)} nodos")
    print(f"  ✓ Tiempo de ejecución: {elapsed_time*1000:.2f} ms")
    print("  ✓ Test pasado\n")


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("EJECUTANDO PRUEBAS DEL SISTEMA DE RUTAS ÓPTIMAS")
    print("=" * 60 + "\n")
    
    tests = [
        test_dijkstra_simple,
        test_dijkstra_no_path,
        test_bellman_ford,
        test_floyd_warshall,
        test_graph_operations,
        test_large_graph_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test falló: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ✗ Error inesperado: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"RESULTADOS: {passed} pruebas pasadas, {failed} pruebas fallidas")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
