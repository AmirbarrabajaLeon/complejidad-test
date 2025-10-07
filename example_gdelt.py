"""
Ejemplo de uso del sistema con datasets GDELT.
Demuestra cómo cargar y analizar eventos geopolíticos.
"""

from models.graph import Graph
from algorithms.dijkstra import dijkstra
from data.gdelt_parser import GDELTParser


def ejemplo_basico():
    """Ejemplo básico de carga y análisis de GDELT."""
    print("=" * 70)
    print("EJEMPLO 1: Carga Básica de Dataset GDELT")
    print("=" * 70)
    
    # Crear grafo
    graph = Graph()
    
    # Cargar dataset GDELT filtrado por USA
    print("\n⏳ Cargando eventos de USA...")
    edges_loaded = graph.load_from_gdelt(
        filepath='data/20251004.export.CSV',
        country_filter='USA',
        max_rows=500,
        max_distance=500.0
    )
    
    # Mostrar estadísticas
    stats = graph.get_stats()
    print(f"\n✓ Dataset cargado:")
    print(f"  • Eventos: {stats['num_nodes']}")
    print(f"  • Conexiones: {stats['num_edges']}")
    print(f"  • Grado promedio: {stats['avg_degree']:.2f}")


def ejemplo_busqueda():
    """Ejemplo de búsqueda de nodos."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Búsqueda de Eventos")
    print("=" * 70)
    
    graph = Graph()
    graph.load_from_gdelt(
        filepath='data/20251004.export.CSV',
        country_filter='USA',
        max_rows=500,
        max_distance=500.0
    )
    
    # Buscar eventos en Delaware
    print("\n🔍 Buscando eventos en Delaware...")
    results = graph.search_nodes('Delaware', limit=10)
    
    print(f"\n✓ Encontrados {len(results)} eventos:")
    for i, node_id in enumerate(results[:5], 1):
        node = graph.get_node(node_id)
        metadata = graph.get_node_metadata(node_id)
        print(f"\n  {i}. ID: {node_id}")
        print(f"     Nombre: {node.name}")
        if metadata:
            print(f"     Ubicación: {metadata.get('location', 'N/A')}")
            print(f"     Fecha: {metadata.get('date', 'N/A')}")


def ejemplo_ruta_optima():
    """Ejemplo de búsqueda de ruta óptima entre eventos."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Ruta Óptima entre Eventos")
    print("=" * 70)
    
    graph = Graph()
    graph.load_from_gdelt(
        filepath='data/20251004.export.CSV',
        country_filter='USA',
        max_rows=1000,
        max_distance=800.0
    )
    
    # Obtener algunos nodos
    all_nodes = graph.get_all_nodes()
    
    if len(all_nodes) < 2:
        print("❌ No hay suficientes nodos para calcular ruta")
        return
    
    # Seleccionar dos nodos con conexiones
    start_node = None
    end_node = None
    
    for node_id in all_nodes:
        neighbors = graph.get_neighbors(node_id)
        if len(neighbors) > 0:
            if start_node is None:
                start_node = node_id
            elif end_node is None:
                end_node = node_id
                break
    
    if not start_node or not end_node:
        print("❌ No se encontraron nodos conectados")
        return
    
    print(f"\n🔍 Calculando ruta entre eventos...")
    print(f"  Origen: {start_node}")
    print(f"  Destino: {end_node}")
    
    # Calcular ruta con Dijkstra
    distance, path = dijkstra(graph, start_node, end_node)
    
    if distance is None:
        print("\n❌ No existe ruta entre estos eventos")
    else:
        print(f"\n✓ Ruta encontrada!")
        print(f"  Distancia total: {distance:.2f} km")
        print(f"  Eventos en la ruta: {len(path)}")
        print(f"\n  Ruta completa:")
        
        for i, node_id in enumerate(path, 1):
            node = graph.get_node(node_id)
            metadata = graph.get_node_metadata(node_id)
            print(f"    {i}. {node_id}")
            if metadata:
                print(f"       📍 {metadata.get('location', 'N/A')}")
                print(f"       📅 {metadata.get('date', 'N/A')}")


def ejemplo_filtrado_pais():
    """Ejemplo de filtrado por país."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Análisis por País")
    print("=" * 70)
    
    # Parsear archivo para obtener países disponibles
    print("\n⏳ Analizando países disponibles...")
    parser = GDELTParser('data/20251004.export.CSV')
    parser.parse(max_rows=1000)
    
    countries = parser.get_available_countries()
    
    print(f"\n✓ Países encontrados: {len(countries)}")
    print("\nTop 10 países por número de eventos:")
    
    # Ordenar por cantidad de eventos
    sorted_countries = sorted(countries, key=lambda x: x[1], reverse=True)
    
    for i, (country, count) in enumerate(sorted_countries[:10], 1):
        print(f"  {i}. {country}: {count} eventos")
    
    # Cargar eventos de un país específico
    if sorted_countries:
        top_country = sorted_countries[0][0]
        print(f"\n📊 Cargando eventos de {top_country}...")
        
        graph = Graph()
        graph.load_from_gdelt(
            filepath='data/20251004.export.CSV',
            country_filter=top_country,
            max_rows=500,
            max_distance=500.0
        )
        
        stats = graph.get_stats()
        print(f"\n✓ Grafo de {top_country}:")
        print(f"  • Eventos: {stats['num_nodes']}")
        print(f"  • Conexiones: {stats['num_edges']}")


def ejemplo_metadata():
    """Ejemplo de acceso a metadata de eventos."""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Exploración de Metadata")
    print("=" * 70)
    
    graph = Graph()
    graph.load_from_gdelt(
        filepath='data/20251004.export.CSV',
        max_rows=100,
        max_distance=1000.0
    )
    
    # Obtener primer nodo con metadata
    all_nodes = graph.get_all_nodes()
    
    if not all_nodes:
        print("❌ No hay nodos cargados")
        return
    
    print(f"\n📋 Mostrando metadata de los primeros 3 eventos:\n")
    
    for i, node_id in enumerate(all_nodes[:3], 1):
        node = graph.get_node(node_id)
        metadata = graph.get_node_metadata(node_id)
        neighbors = graph.get_neighbors(node_id)
        
        print(f"{i}. Evento ID: {node_id}")
        print(f"   Nombre: {node.name}")
        print(f"   Coordenadas: ({node.y:.4f}, {node.x:.4f})")
        
        if metadata:
            print(f"   Metadata:")
            print(f"     • Fecha: {metadata.get('date', 'N/A')}")
            print(f"     • Actor 1: {metadata.get('actor1', 'N/A')}")
            print(f"     • Actor 2: {metadata.get('actor2', 'N/A')}")
            print(f"     • Ubicación: {metadata.get('location', 'N/A')}")
            print(f"     • País: {metadata.get('country', 'N/A')}")
            print(f"     • Goldstein: {metadata.get('goldstein', 'N/A')}")
            if metadata.get('url'):
                print(f"     • URL: {metadata['url'][:60]}...")
        
        print(f"   Conexiones: {len(neighbors)} eventos cercanos")
        print()


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 70)
    print(" " * 20 + "EJEMPLOS DE USO GDELT")
    print("=" * 70)
    
    try:
        ejemplo_basico()
        ejemplo_busqueda()
        ejemplo_ruta_optima()
        ejemplo_filtrado_pais()
        ejemplo_metadata()
        
        print("\n" + "=" * 70)
        print("✓ Todos los ejemplos completados exitosamente")
        print("=" * 70)
        
    except FileNotFoundError:
        print("\n❌ Error: No se encontró el archivo GDELT")
        print("   Asegúrate de tener el archivo '20251004.export.CSV' en la carpeta 'data/'")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == '__main__':
    main()
