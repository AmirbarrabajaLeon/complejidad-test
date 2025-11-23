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
            engine: str = 'dot'  # 'dot' es jerarquico, 'neato' respeta mas las posiciones
    ) -> bool:

        if not self.graphviz_available:
            print("❌ Graphviz no está instalado. Instálalo con: pip install graphviz")
            return False

        try:
            import graphviz

            stats = self.graph.get_stats()
            # Seguridad para no explotar la PC en la demo
            if stats['num_nodes'] > max_nodes:
                print(f"⚠️  El grafo tiene {stats['num_nodes']} nodos.")
                print(f"   Visualizando los primeros {max_nodes} para mantener claridad.")

            # Configuración estética para Tendencias
            dot = graphviz.Digraph(comment='Mapa de Tendencias', engine=engine)
            dot.attr(rankdir='LR')  # Izquierda a Derecha (Línea de tiempo visual)
            dot.attr('node', shape='note', style='filled', fillcolor='lightyellow')  # Forma de "nota" para noticias

            # Obtener nodos a visualizar
            all_nodes = self.graph.get_all_nodes()
            nodes_to_show = all_nodes[:max_nodes]

            # --- CAMBIO CLAVE AQUÍ ---
            for node_id in nodes_to_show:
                node = self.graph.get_node(node_id)

                # LOGICA DE COLORES (SENTIMIENTO)
                fill_color = 'lightyellow'  # Default Neutral

                # Accedemos al atributo tone si existe
                tone = getattr(node, 'tone', 0)

                if tone > 0:
                    fill_color = '#a8e6cf'  # Verde Pastel (Positivo)
                elif tone < 0:
                    fill_color = '#ff8b94'  # Rojo Pastel (Negativo)


                # Intentamos crear una etiqueta bonita:
                # Titular (recortado a 20 chars) + Fecha
                label_text = node_id
                if hasattr(node, 'name') and node.name:
                    short_name = (node.name[:20] + '..') if len(node.name) > 20 else node.name
                    date_text = getattr(node, 'date', '')
                    label_text = f"{short_name}\n({date_text})"

                # Aplicamos el color
                dot.node(node_id, label=label_text, style='filled', fillcolor=fill_color)
                # -------------------------

            # Agregar aristas (Conexiones por similitud)
            edges_added = 0
            for node_id in nodes_to_show:
                for neighbor, weight in self.graph.get_neighbors(node_id):
                    if neighbor in nodes_to_show:
                        # Las aristas más fuertes (mayor similitud) se pintan más gruesas
                        penwidth = str(1 + (weight * 2))
                        dot.edge(node_id, neighbor, label=f'{weight:.2f}', penwidth=penwidth)
                        edges_added += 1

            # Renderizar
            output_path = dot.render(output_file, format=format, cleanup=True)

            print(f"✓ Grafo generado: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error al visualizar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def visualize_path(
        self,
        path: List[str],
        output_file: str = 'path',
        format: str = 'png',
        show_context: bool = True,
        context_depth: int = 1,
        engine: str = 'dot'
    ) -> bool:
       
        if not self.graphviz_available:
            print("❌ Graphviz no está instalado. Instálalo con: pip install graphviz")
            return False
        
        if not path or len(path) < 2:
            print("❌ La ruta debe tener al menos 2 nodos.")
            return False
        
        try:
            import graphviz
            
            # Crear grafo dirigido
            dot = graphviz.Digraph(comment='Ruta Óptima', engine=engine)
            dot.attr(rankdir='LR')
            
            # Conjuntos de nodos
            path_nodes = set(path)
            context_nodes = set()
            
            # Agregar nodos de contexto si se solicita
            if show_context:
                for node in path:
                    for neighbor, _ in self.graph.get_neighbors(node):
                        if neighbor not in path_nodes:
                            context_nodes.add(neighbor)
            
            # Agregar nodos de la ruta (resaltados)
            for i, node_id in enumerate(path):
                if i == 0:
                    # Nodo inicial (verde)
                    dot.node(node_id, node_id, shape='circle', style='filled', 
                            fillcolor='lightgreen', penwidth='3')
                elif i == len(path) - 1:
                    # Nodo final (rojo)
                    dot.node(node_id, node_id, shape='circle', style='filled', 
                            fillcolor='lightcoral', penwidth='3')
                else:
                    # Nodos intermedios (amarillo)
                    dot.node(node_id, node_id, shape='circle', style='filled', 
                            fillcolor='yellow', penwidth='2')
            
            # Agregar nodos de contexto (gris claro)
            for node_id in context_nodes:
                dot.node(node_id, node_id, shape='circle', style='filled', 
                        fillcolor='lightgray')
            
            # Agregar aristas de la ruta (resaltadas)
            total_distance = 0
            for i in range(len(path) - 1):
                weight = self.graph.get_edge_weight(path[i], path[i+1])
                if weight is not None:
                    total_distance += weight
                    dot.edge(path[i], path[i+1], label=f'{weight:.1f}', 
                            color='red', penwidth='3', fontcolor='red')
            
            # Agregar aristas de contexto
            if show_context:
                for node in path:
                    for neighbor, weight in self.graph.get_neighbors(node):
                        if neighbor in context_nodes:
                            dot.edge(node, neighbor, label=f'{weight:.1f}', 
                                   color='gray', style='dashed')
            
            # Agregar información de la ruta
            info = f'Distancia Total: {total_distance:.2f}\\nNodos: {len(path)}'
            dot.attr(label=info, fontsize='14', labelloc='t')
            
            # Renderizar
            dot.render(output_file, format=format, cleanup=True)
            
            print(f"✓ Ruta visualizada exitosamente")
            print(f"  Archivo: {output_file}.{format}")
            print(f"  Nodos en ruta: {len(path)}")
            print(f"  Distancia total: {total_distance:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al visualizar la ruta: {str(e)}")
            return False
    
    def visualize_subgraph(
        self,
        nodes: List[str],
        output_file: str = 'subgraph',
        format: str = 'png',
        highlight_nodes: Optional[List[str]] = None,
        engine: str = 'dot'
    ) -> bool:
       
        if not self.graphviz_available:
            print("❌ Graphviz no está instalado.")
            return False
        
        try:
            import graphviz
            
            dot = graphviz.Digraph(comment='Subgrafo', engine=engine)
            dot.attr(rankdir='LR')
            
            highlight_set = set(highlight_nodes) if highlight_nodes else set()
            
            # Agregar nodos
            for node_id in nodes:
                if node_id in highlight_set:
                    dot.node(node_id, node_id, shape='circle', style='filled', 
                            fillcolor='yellow', penwidth='2')
                else:
                    dot.node(node_id, node_id, shape='circle', style='filled', 
                            fillcolor='lightblue')
            
            # Agregar aristas
            edges_added = 0
            for node_id in nodes:
                for neighbor, weight in self.graph.get_neighbors(node_id):
                    if neighbor in nodes:
                        dot.edge(node_id, neighbor, label=f'{weight:.1f}')
                        edges_added += 1
            
            # Renderizar
            dot.render(output_file, format=format, cleanup=True)
            
            print(f"✓ Subgrafo visualizado exitosamente")
            print(f"  Archivo: {output_file}.{format}")
            print(f"  Nodos: {len(nodes)}")
            print(f"  Aristas: {edges_added}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al visualizar el subgrafo: {str(e)}")
            return False
    
    def create_comparison_visualization(
        self,
        paths: List[tuple],
        output_file: str = 'comparison',
        format: str = 'png'
    ) -> bool:
       
        if not self.graphviz_available:
            print("❌ Graphviz no está instalado.")
            return False
        
        try:
            import graphviz
            
            dot = graphviz.Digraph(comment='Comparación de Rutas')
            dot.attr(rankdir='LR', compound='true')
            
            colors = ['red', 'blue', 'green', 'purple', 'orange']
            
            # Recopilar todos los nodos
            all_nodes = set()
            for _, path, _ in paths:
                all_nodes.update(path)
            
            # Agregar nodos
            for node_id in all_nodes:
                dot.node(node_id, node_id, shape='circle', style='filled', 
                        fillcolor='lightblue')
            
            # Agregar aristas para cada ruta con diferentes colores
            for i, (name, path, distance) in enumerate(paths):
                color = colors[i % len(colors)]
                
                for j in range(len(path) - 1):
                    weight = self.graph.get_edge_weight(path[j], path[j+1])
                    if weight is not None:
                        dot.edge(path[j], path[j+1], 
                               label=f'{weight:.1f}', 
                               color=color, 
                               penwidth='2')
            
            # Agregar leyenda
            legend = "Comparación de Rutas:\\n"
            for i, (name, path, distance) in enumerate(paths):
                color = colors[i % len(colors)]
                legend += f"{name}: {distance:.2f} ({len(path)} nodos)\\n"
            
            dot.attr(label=legend, fontsize='12', labelloc='b')
            
            # Renderizar
            dot.render(output_file, format=format, cleanup=True)
            
            print(f"✓ Comparación visualizada exitosamente")
            print(f"  Archivo: {output_file}.{format}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al crear la comparación: {str(e)}")
            return False
