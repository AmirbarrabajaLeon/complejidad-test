"""
Demostración de visualización con Graphviz.
Muestra cómo usar las funcionalidades de visualización.
"""

from models.graph import Graph
from algorithms.dijkstra import dijkstra
from visualization.graph_visualizer import GraphVisualizer


def main():
    print("=" * 70)
    print(" " * 15 + "DEMO DE VISUALIZACIÓN")
    print(" " * 10 + "Sistema de Rutas Óptimas con Graphviz")
    print("=" * 70)
    
    # Verificar si Graphviz está disponible
    print("\n1. Verificando Graphviz...")
    try:
        import graphviz
        print("   ✓ Librería Python graphviz instalada")
    except ImportError:
        print("   ✗ Librería Python graphviz NO instalada")
        print("   Instala con: pip install graphviz")
        return
    
    # Cargar dataset pequeño
    print("\n2. Cargando dataset de prueba...")
    graph = Graph()
    try:
        graph.load_from_csv('data/city_test_50.csv')
        stats = graph.get_stats()
        print(f"   ✓ Dataset cargado: {stats['num_nodes']} nodos, {stats['num_edges']} aristas")
    except FileNotFoundError:
        print("   ✗ Archivo no encontrado. Ejecuta primero: py data/dataset_generator.py")
        return
    
    # Crear visualizador
    print("\n3. Creando visualizador...")
    visualizer = GraphVisualizer(graph)
    
    if not visualizer.graphviz_available:
        print("   ✗ Graphviz no está disponible en el sistema")
        print("\n   Para instalar Graphviz:")
        print("   1. Descarga desde: https://graphviz.org/download/")
        print("   2. Durante instalación, marca 'Add to PATH'")
        print("   3. Reinicia tu terminal/IDE")
        print("\n   Consulta GRAPHVIZ_SETUP.md para más detalles")
        return
    
    print("   ✓ Graphviz disponible")
    
    # Visualizar grafo completo
    print("\n4. Generando visualización del grafo completo...")
    success = visualizer.visualize_graph(
        output_file='demo_grafo',
        format='png',
        max_nodes=50,
        engine='dot'
    )
    
    if success:
        print("   ✓ Archivo generado: demo_grafo.png")
    
    # Buscar una ruta
    print("\n5. Buscando ruta óptima...")
    start = 'N0_0'
    end = 'N6_6'
    
    distance, path = dijkstra(graph, start, end)
    
    if distance:
        print(f"   ✓ Ruta encontrada: {start} → {end}")
        print(f"   Distancia: {distance:.2f}")
        print(f"   Nodos: {len(path)}")
    else:
        print("   ✗ No se encontró ruta")
        return
    
    # Visualizar la ruta
    print("\n6. Generando visualización de la ruta...")
    success = visualizer.visualize_path(
        path=path,
        output_file='demo_ruta',
        format='png',
        show_context=True
    )
    
    if success:
        print("   ✓ Archivo generado: demo_ruta.png")
    
    # Visualizar subgrafo
    print("\n7. Generando visualización de subgrafo...")
    subgraph_nodes = path + [neighbor for node in path 
                             for neighbor, _ in graph.get_neighbors(node)]
    subgraph_nodes = list(set(subgraph_nodes))[:30]  # Limitar a 30 nodos
    
    success = visualizer.visualize_subgraph(
        nodes=subgraph_nodes,
        output_file='demo_subgrafo',
        format='png',
        highlight_nodes=path
    )
    
    if success:
        print("   ✓ Archivo generado: demo_subgrafo.png")
    
    # Resumen
    print("\n" + "=" * 70)
    print("✓ DEMOSTRACIÓN COMPLETADA")
    print("=" * 70)
    print("\nArchivos generados:")
    print("  1. demo_grafo.png - Grafo completo (50 nodos)")
    print("  2. demo_ruta.png - Ruta encontrada con contexto")
    print("  3. demo_subgrafo.png - Subgrafo relevante")
    print("\nAbre estos archivos con cualquier visor de imágenes.")
    print("\nPara usar la aplicación completa: py main.py")
    print()


if __name__ == '__main__':
    main()
