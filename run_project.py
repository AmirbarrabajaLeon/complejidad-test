import os
import sys


# Aseguramos que Python encuentre las carpetas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.graph import Graph
from data.gdelt_parser import GDELTParser
from visualization.graph_visualizer import GraphVisualizer


def main():
    print("=========================================")
    print("   ANALIZADOR DE TENDENCIAS NOTICIOSAS   ")
    print("=========================================")

    # 1. Configuración
    # Busca tu archivo GDELT. Asegúrate que el nombre sea correcto
    gdelt_file = os.path.join("data", "20251004.export.CSV")

    if not os.path.exists(gdelt_file):
        print(f"❌ ERROR: No encuentro el archivo {gdelt_file}")
        return

    # 2. Carga de Datos (PARSING)
    print("\n[PASO 1] Cargando Dataset...")
    parser = GDELTParser(gdelt_file)
    # OJO: Aquí limitamos a 3000 como dijimos
    num_noticias = parser.parse(max_rows=3000)

    if num_noticias == 0:
        print("❌ No se cargaron noticias. Revisa el archivo.")
        return

    data_list = parser.get_data_for_graph()

    # 3. Construcción del Grafo
    print("\n[PASO 2] Construyendo Grafo Temporal...")
    grafo = Graph()
    grafo.load_from_news_dataset(data_list)

    # Simulamos conexiones (Para la DEMO, conectamos noticias cercanas en la lista)
    # En una versión real usarías TF-IDF, pero esto es para que funcione YA.
    print("   -> Generando conexiones por proximidad temporal...")
    nodes = grafo.get_all_nodes()
    for i in range(len(nodes) - 1):
        # Conectamos cada noticia con las 2 siguientes (simulando hilo temporal)
        current = nodes[i]
        next_node = nodes[i + 1]
        grafo.add_edge(current, next_node, weight=0.9)

        if i + 2 < len(nodes):
            grafo.add_edge(current, nodes[i + 2], weight=0.5)

    stats = grafo.get_stats()
    print(f"   ✅ Grafo creado: {stats['num_nodes']} Nodos, {stats['num_edges']} Aristas")

    # 4. Visualización
    print("\n[PASO 3] Generando Visualización...")
    viz = GraphVisualizer(grafo)

    # Generamos la imagen
    viz.visualize_graph(output_file="mapa_tendencias", format="png", max_nodes=50)

    print("\n=========================================")
    print("¡PROCESO TERMINADO!")
    print("Abre el archivo 'mapa_tendencias.png' para ver el resultado.")
    print("=========================================")


if __name__ == "__main__":
    main()