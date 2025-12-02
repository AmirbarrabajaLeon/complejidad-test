from typing import List, Optional, Set
from models.graph import Graph


class GraphVisualizer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.graphviz_available = self._check_graphviz()

    def _check_graphviz(self) -> bool:
        try:
            import graphviz
            return True
        except ImportError:
            return False

    def visualize_graph(
            self,
            output_file: str = 'graph',
            format: str = 'png',
            max_nodes: int = 300,
            engine: str = 'dot',
            highlight_path: List[str] = None  # <--- NUEVO PARAMETRO
    ) -> bool:

        if not self.graphviz_available:
            print("❌ Graphviz no está instalado.")
            return False

        try:
            import graphviz

            # Configuración estética (Mantenemos la que te gusta)
            dot = graphviz.Digraph(comment='Mapa de Tendencias', engine=engine)
            dot.attr(rankdir='LR')
            dot.attr('node', shape='note', style='filled', fontname='Arial')

            # Conjunto para búsqueda rápida
            path_set = set(highlight_path) if highlight_path else set()

            # Obtener nodos
            all_nodes = self.graph.get_all_nodes()
            nodes_to_show = all_nodes[:max_nodes]

            for node_id in nodes_to_show:
                node = self.graph.get_node(node_id)

                # 1. ESTILO BASE (El que ya funcionaba)
                fill_color = 'lightyellow'
                tone = getattr(node, 'tone', 0)
                if tone > 0:
                    fill_color = '#a8e6cf'  # Verde
                elif tone < 0:
                    fill_color = '#ff8b94'  # Rojo

                border_color = 'black'
                penwidth = '1'

                # 2. ESTILO SI ES PARTE DE LA RUTA (OVERRIDE)
                if highlight_path and node_id in path_set:
                    fill_color = '#fff700'  # Amarillo brillante para resaltar
                    border_color = 'red'  # Borde rojo
                    penwidth = '3'  # Borde grueso

                # Etiqueta bonita
                label_text = node_id
                if hasattr(node, 'name') and node.name:
                    short_name = (node.name[:20] + '..') if len(node.name) > 20 else node.name
                    date_text = getattr(node, 'date', '')
                    label_text = f"{short_name}\n({date_text})"

                dot.node(node_id, label=label_text, style='filled',
                         fillcolor=fill_color, color=border_color, penwidth=penwidth)

            # Agregar aristas
            for node_id in nodes_to_show:
                neighbors = self.graph.get_neighbors(node_id)
                for neighbor, weight in neighbors:
                    if neighbor in nodes_to_show:

                        edge_color = 'black'
                        edge_width = str(1 + (weight * 2))  # Grosor basado en peso original
                        style = 'solid'

                        # LÓGICA PARA PINTAR LA FLECHA DE LA RUTA
                        if highlight_path:
                            # Si ambos nodos están en la ruta Y son consecutivos en la lista
                            try:
                                idx = highlight_path.index(node_id)
                                if idx + 1 < len(highlight_path) and highlight_path[idx + 1] == neighbor:
                                    edge_color = 'red'
                                    edge_width = '4'  # Flecha muy gorda
                            except ValueError:
                                pass  # El nodo no está en la ruta, ignorar

                        # Etiqueta del peso
                        dot.edge(node_id, neighbor, label=f'{weight:.2f}',
                                 color=edge_color, penwidth=edge_width, style=style)

            dot.render(output_file, format=format, cleanup=True)
            return True

        except Exception as e:
            print(f"❌ Error al visualizar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # (Puedes dejar visualize_path y visualize_subgraph aquí abajo si quieres,
    # pero ya no las usaremos para la ruta principal)
    def visualize_subgraph(self, nodes, output_file='subgraph', format='png', highlight_nodes=None):
        # Versión simplificada para centralidad
        return self.visualize_graph(output_file, format, highlight_path=highlight_nodes)