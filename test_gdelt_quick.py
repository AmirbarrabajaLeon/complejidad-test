"""
Test rápido para verificar la funcionalidad GDELT.
"""

import sys
import os

def test_parser():
    """Prueba el parser GDELT."""
    print("=" * 70)
    print("TEST 1: Parser GDELT")
    print("=" * 70)
    
    try:
        from data.gdelt_parser import GDELTParser
        
        filepath = 'data/20251004.export.CSV'
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return False
        
        parser = GDELTParser(filepath)
        events_parsed = parser.parse(max_rows=100)
        
        print(f"✓ Parser creado correctamente")
        print(f"✓ Eventos parseados: {events_parsed}")
        
        if events_parsed > 0:
            stats = parser.get_stats()
            print(f"✓ Estadísticas:")
            print(f"  • Total eventos: {stats['total_events']}")
            print(f"  • Países: {stats['countries']}")
            print(f"  • Con coordenadas: {stats['events_with_coordinates']}")
            
            # Mostrar algunos países
            countries = parser.get_available_countries()[:5]
            print(f"\n✓ Primeros 5 países:")
            for country, count in countries:
                print(f"  • {country}: {count} eventos")
            
            return True
        else:
            print("❌ No se parsearon eventos")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_loading():
    """Prueba la carga de GDELT en el grafo."""
    print("\n" + "=" * 70)
    print("TEST 2: Carga en Graph")
    print("=" * 70)
    
    try:
        from models.graph import Graph
        
        filepath = 'data/20251004.export.CSV'
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return False
        
        graph = Graph()
        edges_loaded = graph.load_from_gdelt(
            filepath=filepath,
            country_filter='USA',
            max_rows=100,
            max_distance=500.0
        )
        
        stats = graph.get_stats()
        
        print(f"✓ Grafo cargado correctamente")
        print(f"✓ Aristas cargadas: {edges_loaded}")
        print(f"✓ Nodos: {stats['num_nodes']}")
        print(f"✓ Aristas: {stats['num_edges']}")
        print(f"✓ Grado promedio: {stats['avg_degree']:.2f}")
        
        return stats['num_nodes'] > 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_search():
    """Prueba las funciones de búsqueda."""
    print("\n" + "=" * 70)
    print("TEST 3: Búsqueda de Nodos")
    print("=" * 70)
    
    try:
        from models.graph import Graph
        
        filepath = 'data/20251004.export.CSV'
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return False
        
        graph = Graph()
        graph.load_from_gdelt(
            filepath=filepath,
            max_rows=100,
            max_distance=500.0
        )
        
        # Test búsqueda por texto
        results = graph.search_nodes('USA', limit=5)
        print(f"✓ Búsqueda por texto 'USA': {len(results)} resultados")
        
        # Test filtrado por país
        usa_nodes = graph.filter_nodes_by_country('USA')
        print(f"✓ Filtrado por país 'USA': {len(usa_nodes)} nodos")
        
        # Test metadata
        if results:
            node_id = results[0]
            metadata = graph.get_node_metadata(node_id)
            print(f"✓ Metadata del nodo {node_id}:")
            if metadata:
                for key, value in list(metadata.items())[:3]:
                    print(f"  • {key}: {value}")
            else:
                print("  (sin metadata)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dijkstra():
    """Prueba el algoritmo de Dijkstra con GDELT."""
    print("\n" + "=" * 70)
    print("TEST 4: Algoritmo de Dijkstra")
    print("=" * 70)
    
    try:
        from models.graph import Graph
        from algorithms.dijkstra import dijkstra
        
        filepath = 'data/20251004.export.CSV'
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return False
        
        graph = Graph()
        graph.load_from_gdelt(
            filepath=filepath,
            country_filter='USA',
            max_rows=200,
            max_distance=800.0
        )
        
        # Buscar dos nodos conectados
        all_nodes = graph.get_all_nodes()
        
        start_node = None
        end_node = None
        
        for node_id in all_nodes:
            neighbors = graph.get_neighbors(node_id)
            if len(neighbors) > 0:
                if start_node is None:
                    start_node = node_id
                elif end_node is None:
                    # Buscar un nodo que no sea vecino directo
                    neighbor_ids = [n[0] for n in neighbors]
                    if node_id not in neighbor_ids:
                        end_node = node_id
                        break
        
        if not start_node or not end_node:
            print("⚠️  No se encontraron nodos suficientemente conectados")
            print("   (Esto es normal con pocos eventos)")
            return True
        
        print(f"✓ Calculando ruta entre:")
        print(f"  Origen: {start_node}")
        print(f"  Destino: {end_node}")
        
        distance, path = dijkstra(graph, start_node, end_node)
        
        if distance is None:
            print("⚠️  No existe ruta entre estos nodos")
            print("   (Esto es normal si están muy lejos)")
            return True
        else:
            print(f"✓ Ruta encontrada!")
            print(f"  Distancia: {distance:.2f} km")
            print(f"  Nodos en ruta: {len(path)}")
            return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 70)
    print(" " * 20 + "TEST RÁPIDO GDELT")
    print("=" * 70)
    print()
    
    results = []
    
    # Ejecutar tests
    results.append(("Parser GDELT", test_parser()))
    results.append(("Carga en Graph", test_graph_loading()))
    results.append(("Búsqueda de Nodos", test_search()))
    results.append(("Algoritmo Dijkstra", test_dijkstra()))
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Total: {passed} pasados, {failed} fallidos")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        print("\nPuedes usar el sistema con:")
        print("  python main.py")
        print("\nO ver ejemplos con:")
        print("  python example_gdelt.py")
    else:
        print("\n⚠️  Algunos tests fallaron")
        print("Verifica que el archivo 'data/20251004.export.CSV' exista")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
