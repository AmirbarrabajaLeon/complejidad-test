"""
Demostración rápida del sistema de rutas óptimas.
Ejecuta un ejemplo completo en segundos.
"""

from models.graph import Graph
from algorithms.dijkstra import dijkstra
import time


def main():
    print("=" * 70)
    print(" " * 15 + "DEMOSTRACIÓN RÁPIDA")
    print(" " * 10 + "Sistema de Rutas Óptimas - Dijkstra")
    print("=" * 70)
    
    # Cargar dataset
    print("\n📂 Cargando dataset de prueba (50 nodos)...")
    graph = Graph()
    edges_loaded = graph.load_from_csv('data/city_test_50.csv')
    
    stats = graph.get_stats()
    print(f"✓ Dataset cargado:")
    print(f"  • Nodos: {stats['num_nodes']}")
    print(f"  • Aristas: {stats['num_edges']}")
    print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
    
    # Buscar ruta
    print("\n🔍 Buscando ruta óptima...")
    print(f"  Origen: N0_0")
    print(f"  Destino: N6_6")
    
    start_time = time.time()
    distance, path = dijkstra(graph, 'N0_0', 'N6_6')
    elapsed = time.time() - start_time
    
    # Mostrar resultado
    print(f"\n✓ ¡Ruta encontrada!")
    print(f"\n  📍 Distancia total: {distance:.2f} unidades")
    print(f"  🚗 Nodos en la ruta: {len(path)}")
    print(f"  ⚡ Tiempo de cálculo: {elapsed*1000:.2f} ms")
    
    print(f"\n  📋 Ruta completa:")
    print(f"     {' → '.join(path)}")
    
    # Detalles por segmento
    print(f"\n  📊 Detalles por segmento:")
    for i in range(len(path) - 1):
        weight = graph.get_edge_weight(path[i], path[i+1])
        print(f"     {path[i]:8} → {path[i+1]:8} : {weight:6.2f} unidades")
    
    print("\n" + "=" * 70)
    print("✓ Demostración completada exitosamente")
    print("=" * 70)
    print("\nPara usar la aplicación completa, ejecuta: py main.py")
    print()


if __name__ == '__main__':
    main()
