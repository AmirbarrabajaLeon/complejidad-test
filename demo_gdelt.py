"""
Demostración rápida del sistema GDELT.
Muestra las capacidades principales sin interacción del usuario.
"""

import time
from models.graph import Graph
from algorithms.dijkstra import dijkstra


def print_section(title):
    """Imprime un separador de sección."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def demo():
    """Ejecuta una demostración completa del sistema."""
    
    print_section("🌍 DEMOSTRACIÓN DEL SISTEMA GDELT")
    
    print("Este script demuestra las capacidades del sistema refactorizado")
    print("para trabajar con datasets GDELT de eventos geopolíticos.\n")
    
    input("Presiona Enter para comenzar...")
    
    # ========================================================================
    # PASO 1: Cargar dataset GDELT
    # ========================================================================
    print_section("PASO 1: Cargando Dataset GDELT")
    
    print("Configuración:")
    print("  • Archivo: 20251004.export.CSV")
    print("  • Filtro: USA (solo eventos de Estados Unidos)")
    print("  • Eventos: 500")
    print("  • Distancia máxima: 600 km")
    print("\n⏳ Cargando...")
    
    start_time = time.time()
    
    graph = Graph()
    try:
        edges_loaded = graph.load_from_gdelt(
            filepath='data/20251004.export.CSV',
            country_filter='USA',
            max_rows=500,
            max_distance=600.0
        )
        
        elapsed = time.time() - start_time
        stats = graph.get_stats()
        
        print(f"\n✓ Dataset cargado en {elapsed:.2f} segundos")
        print(f"\n📊 Estadísticas del grafo:")
        print(f"  • Eventos (nodos): {stats['num_nodes']}")
        print(f"  • Conexiones (aristas): {stats['num_edges']}")
        print(f"  • Grado promedio: {stats['avg_degree']:.2f}")
        print(f"  • Densidad: {stats['num_edges'] / (stats['num_nodes'] * (stats['num_nodes'] - 1)):.4f}")
        
    except FileNotFoundError:
        print("\n❌ Error: No se encontró el archivo GDELT")
        print("   Asegúrate de tener '20251004.export.CSV' en la carpeta 'data/'")
        return
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return
    
    input("\nPresiona Enter para continuar...")
    
    # ========================================================================
    # PASO 2: Búsqueda de eventos
    # ========================================================================
    print_section("PASO 2: Búsqueda de Eventos")
    
    print("🔍 Buscando eventos que contengan 'Delaware'...\n")
    
    results = graph.search_nodes('Delaware', limit=10)
    
    if results:
        print(f"✓ Se encontraron {len(results)} eventos:\n")
        
        for i, node_id in enumerate(results[:5], 1):
            node = graph.get_node(node_id)
            metadata = graph.get_node_metadata(node_id)
            
            print(f"{i}. ID: {node_id}")
            print(f"   Nombre: {node.name[:60]}...")
            if metadata:
                print(f"   📍 Ubicación: {metadata.get('location', 'N/A')}")
                print(f"   📅 Fecha: {metadata.get('date', 'N/A')}")
                print(f"   🎯 Goldstein: {metadata.get('goldstein', 'N/A')}")
            print()
    else:
        print("❌ No se encontraron eventos")
    
    input("Presiona Enter para continuar...")
    
    # ========================================================================
    # PASO 3: Filtrado por país
    # ========================================================================
    print_section("PASO 3: Filtrado por País")
    
    print("🌎 Filtrando eventos de USA...\n")
    
    usa_events = graph.filter_nodes_by_country('USA')
    
    print(f"✓ Se encontraron {len(usa_events)} eventos de USA")
    print(f"\nMostrando los primeros 5:\n")
    
    for i, node_id in enumerate(usa_events[:5], 1):
        node = graph.get_node(node_id)
        metadata = graph.get_node_metadata(node_id)
        
        print(f"{i}. {node_id}")
        if metadata:
            print(f"   📍 {metadata.get('location', 'N/A')}")
        print()
    
    input("Presiona Enter para continuar...")
    
    # ========================================================================
    # PASO 4: Detalles de un evento
    # ========================================================================
    print_section("PASO 4: Detalles de un Evento")
    
    if usa_events:
        sample_id = usa_events[0]
        node = graph.get_node(sample_id)
        metadata = graph.get_node_metadata(sample_id)
        neighbors = graph.get_neighbors(sample_id)
        
        print(f"📋 Evento: {sample_id}\n")
        print(f"Nombre: {node.name}")
        print(f"Coordenadas: ({node.y:.4f}, {node.x:.4f})")
        
        if metadata:
            print(f"\nMetadata:")
            print(f"  • Fecha: {metadata.get('date', 'N/A')}")
            print(f"  • Actor 1: {metadata.get('actor1', 'N/A')}")
            print(f"  • Actor 2: {metadata.get('actor2', 'N/A')}")
            print(f"  • Ubicación: {metadata.get('location', 'N/A')}")
            print(f"  • País: {metadata.get('country', 'N/A')}")
            print(f"  • Goldstein: {metadata.get('goldstein', 'N/A')}")
            if metadata.get('url'):
                print(f"  • URL: {metadata['url'][:60]}...")
        
        print(f"\nConexiones: {len(neighbors)} eventos cercanos")
        
        if neighbors:
            print(f"\nPrimeros 3 eventos cercanos:")
            for neighbor_id, distance in neighbors[:3]:
                print(f"  → {neighbor_id} ({distance:.2f} km)")
    
    input("\nPresiona Enter para continuar...")
    
    # ========================================================================
    # PASO 5: Búsqueda de ruta óptima
    # ========================================================================
    print_section("PASO 5: Búsqueda de Ruta Óptima")
    
    print("🛣️  Buscando ruta más corta entre dos eventos...\n")
    
    # Buscar dos nodos con buenas conexiones
    all_nodes = graph.get_all_nodes()
    
    start_node = None
    end_node = None
    
    # Buscar nodos con conexiones
    for node_id in all_nodes:
        neighbors = graph.get_neighbors(node_id)
        if len(neighbors) >= 2:
            if start_node is None:
                start_node = node_id
            elif end_node is None:
                # Buscar un nodo que no sea vecino directo
                neighbor_ids = [n[0] for n in neighbors]
                if node_id not in neighbor_ids and start_node not in neighbor_ids:
                    end_node = node_id
                    break
    
    if not start_node or not end_node:
        # Fallback: usar cualquier par de nodos
        if len(all_nodes) >= 2:
            start_node = all_nodes[0]
            end_node = all_nodes[min(10, len(all_nodes) - 1)]
    
    if start_node and end_node:
        print(f"Origen: {start_node}")
        start_meta = graph.get_node_metadata(start_node)
        if start_meta:
            print(f"  📍 {start_meta.get('location', 'N/A')}")
        
        print(f"\nDestino: {end_node}")
        end_meta = graph.get_node_metadata(end_node)
        if end_meta:
            print(f"  📍 {end_meta.get('location', 'N/A')}")
        
        print("\n⏳ Calculando ruta con algoritmo de Dijkstra...")
        
        start_time = time.time()
        distance, path = dijkstra(graph, start_node, end_node)
        elapsed = time.time() - start_time
        
        if distance is None:
            print("\n❌ No existe ruta entre estos eventos")
            print("   (Están demasiado lejos o no hay conexión)")
        else:
            print(f"\n✓ Ruta encontrada en {elapsed*1000:.2f} ms")
            print(f"\n📏 Distancia total: {distance:.2f} km")
            print(f"🔢 Eventos en la ruta: {len(path)}")
            
            print(f"\n🗺️  Ruta completa:\n")
            for i, node_id in enumerate(path, 1):
                node = graph.get_node(node_id)
                meta = graph.get_node_metadata(node_id)
                
                symbol = "🟢" if i == 1 else "🔴" if i == len(path) else "🟡"
                print(f"  {symbol} {i}. {node_id}")
                if meta:
                    print(f"      📍 {meta.get('location', 'N/A')}")
                
                # Mostrar distancia al siguiente
                if i < len(path):
                    next_node = path[i]
                    segment_dist = graph.get_edge_weight(node_id, next_node)
                    if segment_dist:
                        print(f"      ↓ {segment_dist:.2f} km")
                print()
    else:
        print("❌ No hay suficientes nodos para calcular ruta")
    
    input("Presiona Enter para continuar...")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print_section("✨ RESUMEN DE LA DEMOSTRACIÓN")
    
    print("Has visto las capacidades principales del sistema:\n")
    print("✓ Carga de datasets GDELT con filtrado por país")
    print("✓ Búsqueda de eventos por texto")
    print("✓ Filtrado de eventos por código de país")
    print("✓ Exploración detallada de metadata")
    print("✓ Cálculo de rutas óptimas con Dijkstra")
    
    print("\n" + "=" * 70)
    print("🚀 PRÓXIMOS PASOS")
    print("=" * 70 + "\n")
    
    print("1. Ejecuta la aplicación principal:")
    print("   py main.py")
    print("\n2. Selecciona opción 3 para cargar tu dataset GDELT")
    print("\n3. Explora con la opción 5 (Búsqueda de nodos)")
    print("\n4. Calcula rutas con la opción 6 (Dijkstra)")
    print("\n5. Lee la documentación completa:")
    print("   - GDELT_USAGE.md (guía de uso)")
    print("   - REFACTORIZACION.md (detalles técnicos)")
    print("   - README_GDELT.md (resumen general)")
    
    print("\n" + "=" * 70)
    print("¡Gracias por usar el Sistema de Rutas Óptimas GDELT!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
