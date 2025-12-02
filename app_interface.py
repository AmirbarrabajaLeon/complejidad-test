import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import webbrowser
import matplotlib.pyplot as plt
import tkinter as tk
from collections import Counter
import math

# --- CONFIGURACIÓN DE SEGURIDAD PARA GRAPHVIZ ---
path_graphviz = r"C:\Program Files\Graphviz\bin"
if os.path.exists(path_graphviz):
    os.environ["PATH"] += os.pathsep + path_graphviz
# ------------------------------------------------

from models.graph import Graph
from data.gdelt_parser import GDELTParser
from visualization.graph_visualizer import GraphVisualizer
from algorithms.merge_sort import merge_sort

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NewsAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Análisis de Tendencias - TB2 Final Pro")
        self.geometry("1300x850")

        self.all_data = []
        self.current_filtered_data = []
        self.original_pil_image = None
        self.current_tk_image = None
        self.temp_graph_obj = None  # Guardamos el objeto grafo para algoritmos

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === PANEL IZQUIERDO ===
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="PANEL DE CONTROL", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_load = ctk.CTkButton(self.sidebar, text="1. Cargar Dataset", command=self.cargar_datos)
        self.btn_load.grid(row=1, column=0, padx=20, pady=10)

        self.lbl_search = ctk.CTkLabel(self.sidebar, text="Búsqueda Específica:", anchor="w")
        self.lbl_search.grid(row=2, column=0, padx=20, pady=(20, 0))
        self.entry_search = ctk.CTkEntry(self.sidebar, placeholder_text="Ej: Peru")
        self.entry_search.grid(row=3, column=0, padx=20, pady=5)

        self.btn_analyze = ctk.CTkButton(self.sidebar, text="2. Analizar Tema", fg_color="green",
                                         command=self.ejecutar_analisis)
        self.btn_analyze.grid(row=4, column=0, padx=20, pady=20)

        self.btn_top10 = ctk.CTkButton(self.sidebar, text="3. Ver Top 10 Global", fg_color="#d35400",
                                       hover_color="#e67e22", command=self.generar_top_10_global)
        self.btn_top10.grid(row=5, column=0, padx=20, pady=10)

        # --- NUEVOS BOTONES DE ALGORITMOS AVANZADOS ---
        self.lbl_algo = ctk.CTkLabel(self.sidebar, text="Algoritmos Avanzados:", anchor="w", font=("Arial", 12, "bold"))
        self.lbl_algo.grid(row=6, column=0, padx=20, pady=(20, 5))

        self.btn_dijkstra = ctk.CTkButton(self.sidebar, text="📍 Ruta Narrativa (Dijkstra)", fg_color="#2980b9",
                                          command=self.mostrar_ruta_narrativa)
        self.btn_dijkstra.grid(row=7, column=0, padx=20, pady=5)

        self.btn_floyd = ctk.CTkButton(self.sidebar, text="⭐ Noticia Central (Floyd)", fg_color="#8e44ad",
                                       command=self.mostrar_noticia_central)
        self.btn_floyd.grid(row=8, column=0, padx=20, pady=5)
        # ----------------------------------------------

        # PANEL DE ZOOM (OCULTO)
        self.zoom_panel = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.zoom_panel.grid(row=9, column=0, pady=20, sticky="ew")

        self.lbl_zoom = ctk.CTkLabel(self.zoom_panel, text="Zoom: 100%", anchor="w")
        self.lbl_zoom.pack(pady=(5, 0))

        self.slider_zoom = ctk.CTkSlider(self.zoom_panel, from_=0.1, to=2.0, number_of_steps=19,
                                         command=self.actualizar_zoom)
        self.slider_zoom.set(1.0)
        self.slider_zoom.pack(pady=5)
        self.zoom_panel.grid_remove()

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Estado: Esperando...", text_color="gray", wraplength=200)
        self.lbl_status.grid(row=10, column=0, padx=20, pady=20, sticky="s")

        # === PANEL DERECHO ===
        self.tabview = ctk.CTkTabview(self, command=self.al_cambiar_pestana)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_stats = self.tabview.add("Estadísticas")
        self.tab_links = self.tabview.add("Fuentes y Enlaces")
        self.tab_graph = self.tabview.add("Grafo Temporal")

        # TAB 1: ESTADÍSTICAS
        self.tab_stats.grid_columnconfigure(0, weight=1)
        self.tab_stats.grid_rowconfigure(1, weight=1)
        self.frame_vs = ctk.CTkFrame(self.tab_stats)
        self.frame_vs.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.entry_term1 = ctk.CTkEntry(self.frame_vs, placeholder_text="Término A")
        self.entry_term1.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkLabel(self.frame_vs, text="VS").pack(side="left", padx=5)
        self.entry_term2 = ctk.CTkEntry(self.frame_vs, placeholder_text="Término B")
        self.entry_term2.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(self.frame_vs, text="Comparar", command=self.comparar_terminos).pack(side="left", padx=5)
        self.lbl_chart = ctk.CTkLabel(self.tab_stats, text="")
        self.lbl_chart.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # TAB 2: LINKS
        self.tab_links.grid_columnconfigure(0, weight=1)
        self.tab_links.grid_rowconfigure(0, weight=1)
        self.scroll_links = ctk.CTkScrollableFrame(self.tab_links, label_text="Noticias Relacionadas")
        self.scroll_links.grid(row=0, column=0, sticky="nsew")

        # TAB 3: GRAFO
        self.tab_graph.grid_columnconfigure(0, weight=1)
        self.tab_graph.grid_rowconfigure(0, weight=1)
        self.graph_container = ctk.CTkFrame(self.tab_graph)
        self.graph_container.grid(row=0, column=0, sticky="nsew")
        self.graph_container.grid_rowconfigure(0, weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.graph_container, bg="#2b2b2b", highlightthickness=0)
        self.v_scroll = ctk.CTkScrollbar(self.graph_container, orientation="vertical", command=self.canvas.yview)
        self.h_scroll = ctk.CTkScrollbar(self.graph_container, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas_text = self.canvas.create_text(400, 300, text="Realiza una búsqueda para ver el grafo.",
                                                   fill="white", font=("Arial", 16))

    # --- FUNCIONES AUXILIARES ---
    def _obtener_palabras_limpias(self, data_item):
        full_text = (data_item['headline'] + " " + data_item['content']).lower()
        for char in [".", ",", ":", ";", '"', "'", "-", "(", ")", "!", "?", "/", "[", "]"]:
            full_text = full_text.replace(char, " ")
        return full_text.split()

    def _calcular_similitud_jaccard(self, text1, text2):
        """Algoritmo de Fuerza Bruta para calcular similitud de conjuntos"""
        # Tokenización simple
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())

        # Filtramos palabras irrelevantes muy cortas
        set1 = {w for w in set1 if len(w) > 3}
        set2 = {w for w in set2 if len(w) > 3}

        if not set1 or not set2: return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    # --- ALGORITMOS EN LA CLASE PARA ESTABILIDAD ---
    def _dijkstra(self, graph, start_id, end_id):
        """Implementación interna de Dijkstra para asegurar compatibilidad"""
        # Inicialización
        distances = {node: float('inf') for node in graph.nodes}
        previous = {node: None for node in graph.nodes}
        distances[start_id] = 0
        unvisited = list(graph.nodes.keys())

        while unvisited:
            # Seleccionar nodo con menor distancia (Greedy)
            # Esto se podría optimizar con PriorityQueue (Heap), pero lista es válida para <100 nodos
            current_node = min(unvisited, key=lambda node: distances[node])

            if distances[current_node] == float('inf'):
                break  # No hay camino

            if current_node == end_id:
                break  # Llegamos

            unvisited.remove(current_node)

            # Relajar aristas
            for neighbor, weight in graph.get_neighbors(current_node):
                alt = distances[current_node] + weight
                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    previous[neighbor] = current_node

        # Reconstruir camino
        path = []
        current = end_id
        if previous[current] is not None or current == start_id:
            while current is not None:
                path.insert(0, current)
                current = previous[current]
        return path

    def _floyd_warshall_centrality(self, graph):
        """Implementación de Floyd-Warshall para encontrar nodo central"""
        nodes = list(graph.nodes.keys())
        n = len(nodes)
        if n == 0: return None

        # Mapeo de ID a índice
        id_to_idx = {node_id: i for i, node_id in enumerate(nodes)}

        # Inicializar matriz de distancias
        dist = [[float('inf')] * n for _ in range(n)]

        # Distancia a sí mismo es 0
        for i in range(n):
            dist[i][i] = 0

        # Llenar con pesos existentes
        for u_id in nodes:
            u = id_to_idx[u_id]
            for v_id, weight in graph.get_neighbors(u_id):
                if v_id in id_to_idx:
                    v = id_to_idx[v_id]
                    dist[u][v] = weight

        # Algoritmo O(V^3)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        # Calcular centralidad (menor suma de distancias a otros)
        min_total_dist = float('inf')
        central_node = None

        for i in range(n):
            total_dist = sum(d for d in dist[i] if d != float('inf'))
            if total_dist < min_total_dist and total_dist > 0:
                min_total_dist = total_dist
                central_node = nodes[i]

        return central_node

    def al_cambiar_pestana(self):
        tab_actual = self.tabview.get()
        if tab_actual == "Grafo Temporal":
            self.zoom_panel.grid()
        else:
            self.zoom_panel.grid_remove()

    def cargar_datos(self):
        self.lbl_status.configure(text="Cargando CSV...", text_color="yellow")
        self.update()
        try:
            filepath = os.path.join("data", "20251004.export.CSV")
            if not os.path.exists(filepath):
                self.lbl_status.configure(text="ERROR: Falta CSV", text_color="red")
                return

            parser = GDELTParser(filepath)
            parser.parse(max_rows=5000)
            self.all_data = parser.get_data_for_graph()
            self.lbl_status.configure(text=f"Dataset OK: {len(self.all_data)} noticias", text_color="green")
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {str(e)}", text_color="red")

    def ejecutar_analisis(self):
        if not self.all_data:
            self.lbl_status.configure(text="¡Carga datos primero!", text_color="orange")
            return

        keyword = self.entry_search.get().lower().strip()
        self.lbl_status.configure(text="Procesando...", text_color="yellow")
        self.update()

        filtered = []
        if keyword:
            filtered = [d for d in self.all_data if keyword in d['headline'].lower() or keyword in d['content'].lower()]
            filtered = filtered[:100]  # Limitamos a 100 para claridad
        else:
            filtered = self.all_data[:50]

        self.current_filtered_data = filtered

        if not filtered:
            self.lbl_status.configure(text="No se encontraron resultados.", text_color="orange")
            return

        try:
            # CAMBIO CRÍTICO: Ordenar por Fecha Y LUEGO por ID para desempatar eventos del mismo día
            # Esto crea una línea de tiempo estricta y correcta
            filtered = merge_sort(filtered, key_func=lambda x: (x['date'], int(x['id'])))
        except Exception as e:
            print(f"Error sorting: {e}")

        self.temp_graph_obj = Graph()
        self.temp_graph_obj.load_from_news_dataset(filtered)
        nodes = self.temp_graph_obj.get_all_nodes()

        # --- CONSTRUCCIÓN INTELIGENTE DEL GRAFO ---
        WINDOW_SIZE = 3
        for i in range(len(nodes)):
            node_a = self.temp_graph_obj.get_node(nodes[i])

            for j in range(1, WINDOW_SIZE + 1):
                if i + j < len(nodes):
                    node_b = self.temp_graph_obj.get_node(nodes[i + j])

                    # 1. Distancia Temporal (Base)
                    temporal_cost = 1.0 / j  # Vecino cercano cuesta más (1.0), lejano cuesta menos (0.5)
                    # Invertimos lógica para Dijkstra: Queremos que saltar sea "barato" si es similar

                    # 2. Similitud Semántica (Jaccard)
                    similitud = self._calcular_similitud_jaccard(node_a.content, node_b.content)

                    # 3. Diferencia de Tono
                    tone_diff = abs(node_a.tone - node_b.tone)

                    # FÓRMULA MAESTRA DEL PESO
                    # Peso = (Costo Temporal) * (Factor de No-Similitud)
                    # Si son muy similares, el peso baja drásticamente (camino preferido)
                    weight = (1.0 / j) * (1.0 - similitud) + (tone_diff * 0.1)

                    # Aseguramos peso mínimo positivo
                    weight = max(0.1, round(weight, 2))

                    self.temp_graph_obj.add_edge(nodes[i], nodes[i + j], weight=weight)

        try:
            viz = GraphVisualizer(self.temp_graph_obj)
            output = "grafo_temp"
            success = viz.visualize_graph(output_file=output, format="png", max_nodes=100, engine='dot')

            if success:
                self.cargar_imagen_memoria(output + ".png")
                self.generar_lista_links(filtered)  # Pasamos lista normal
                self.lbl_status.configure(text=f"Grafo generado: {len(nodes)} nodos", text_color="white")
                self.tabview.set("Grafo Temporal")
            else:
                self.lbl_status.configure(text="Error Graphviz", text_color="red")
        except Exception as e:
            self.lbl_status.configure(text=f"Error Viz: {e}", text_color="red")

    # --- NUEVAS FUNCIONES DE ALGORITMOS VISUALES ---
    def mostrar_ruta_narrativa(self):
        """Ejecuta Dijkstra y muestra el camino"""
        if not self.temp_graph_obj:
            self.lbl_status.configure(text="Primero analiza un tema.", text_color="orange")
            return

        nodes = self.temp_graph_obj.get_all_nodes()
        if len(nodes) < 2: return

        start_node = nodes[0]  # Noticia más antigua
        end_node = nodes[-1]  # Noticia más reciente

        self.lbl_status.configure(text="Calculando Ruta Narrativa (Dijkstra)...", text_color="yellow")
        self.update()

        path = self._dijkstra(self.temp_graph_obj, start_node, end_node)

        if not path:
            self.lbl_status.configure(text="No hay camino narrativo claro.", text_color="orange")
            return

        # Visualizar Ruta
        viz = GraphVisualizer(self.temp_graph_obj)
        output = "ruta_narrativa"
        success = viz.visualize_path(path, output_file=output, format="png")

        if success:
            self.cargar_imagen_memoria(output + ".png")

            # Filtrar la lista de la derecha para mostrar SOLO la ruta
            path_data = [d for d in self.current_filtered_data if str(d['id']) in path]
            self.generar_lista_links(path_data, title="RUTA NARRATIVA (DIJKSTRA)")

            self.lbl_status.configure(text=f"Ruta óptima encontrada: {len(path)} pasos.", text_color="#2980b9")
            self.tabview.set("Grafo Temporal")

    def mostrar_noticia_central(self):
        """Ejecuta Floyd-Warshall y destaca el nodo central"""
        if not self.temp_graph_obj:
            self.lbl_status.configure(text="Primero analiza un tema.", text_color="orange")
            return

        self.lbl_status.configure(text="Calculando Centralidad (Floyd-Warshall)...", text_color="yellow")
        self.update()

        central_node_id = self._floyd_warshall_centrality(self.temp_graph_obj)

        if central_node_id:
            # Visualizar Subgrafo resaltando el centro
            viz = GraphVisualizer(self.temp_graph_obj)
            output = "noticia_central"
            # Mostramos vecinos del central para contexto
            neighbors = [n[0] for n in self.temp_graph_obj.get_neighbors(central_node_id)]
            nodes_to_show = [central_node_id] + neighbors

            success = viz.visualize_subgraph(nodes_to_show, output_file=output,
                                             highlight_nodes=[central_node_id], format="png")

            if success:
                self.cargar_imagen_memoria(output + ".png")

                # Mostrar info en la lista
                central_data = [d for d in self.current_filtered_data if str(d['id']) == central_node_id]
                self.generar_lista_links(central_data, title="NOTICIA CENTRAL (FLOYD-WARSHALL)")

                # Popup informativo
                tk.messagebox.showinfo("Análisis de Centralidad",
                                       f"La noticia más influyente del periodo es:\n\n{central_data[0]['headline']}\n\n"
                                       f"Motivo: Tiene la menor distancia promedio hacia todos los eventos futuros.")

                self.lbl_status.configure(text="Centralidad calculada.", text_color="#8e44ad")

    def generar_top_10_global(self):
        if not self.all_data:
            self.lbl_status.configure(text="¡Carga datos primero!", text_color="orange")
            return

        self.lbl_status.configure(text="Calculando Top 10 Global...", text_color="yellow")
        self.update()

        # 1. Stopwords (Lista ampliada)
        stopwords = {
            "the", "of", "to", "and", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with",
            "as", "i", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "hot", "but",
            "some", "what", "there", "we", "can", "out", "other", "were", "all", "your", "when", "up", "use", "word",
            "how", "said", "an", "each", "she", "which", "do", "their", "time", "if", "will", "way", "about", "many",
            "then", "them", "would", "write", "like", "so", "these", "her", "long", "make", "thing", "see", "him",
            "two", "has", "look", "more", "day", "could", "go", "come", "did", "my", "sound", "no", "most", "number",
            "who", "over", "know", "water", "than", "call", "first", "people", "may", "down", "side", "been", "now",
            "find", "new", "part", "after", "says", "images", "news", "report", "daily", "times", "post", "view",
            "video", "source", "link", "read", "share", "http", "https", "chars", "brief", "full", "story", "fuente",
            "html", "say", "year", "state"
        }

        all_words = []
        for d in self.all_data:
            words = self._obtener_palabras_limpias(d)
            clean_words = [w for w in words if w not in stopwords and len(w) > 3]
            all_words.extend(clean_words)

        # Hash Map Counting
        counter = Counter(all_words)
        items = list(counter.items())

        try:
            # Divide & Conquer Sorting
            sorted_items = merge_sort(items, key_func=lambda x: x[1])
            top_10 = sorted_items[-10:]
            top_10.reverse()
        except Exception as e:
            print(f"Error en Merge Sort: {e}, usando backup...")
            top_10 = counter.most_common(10)

        words_plot = [x[0].upper() for x in top_10]
        counts_plot = [x[1] for x in top_10]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(words_plot, counts_plot, color='#9b59b6')
        ax.invert_yaxis()
        ax.bar_label(bars, padding=3, color='white', fontsize=10, fontweight='bold')
        ax.set_title("TOP 10 TENDENCIAS GLOBALES", color='white', fontsize=14)
        ax.margins(x=0.1)

        filename = "chart_top10.png"
        plt.savefig(filename, facecolor='#2b2b2b', bbox_inches='tight')
        plt.close()

        if os.path.exists(filename):
            pil_img = Image.open(filename)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(600, 400))
            self.lbl_chart.configure(image=ctk_img, text="")
            self.lbl_status.configure(text="Top 10 generado.", text_color="white")
            self.tabview.set("Estadísticas")

    def cargar_imagen_memoria(self, path):
        if os.path.exists(path):
            self.original_pil_image = Image.open(path)
            self.slider_zoom.set(1.0)
            self.actualizar_zoom(1.0)

    def actualizar_zoom(self, value):
        if self.original_pil_image is None: return
        scale = float(value)
        self.lbl_zoom.configure(text=f"Zoom: {int(scale * 100)}%")
        orig_w, orig_h = self.original_pil_image.size
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        resized_pil = self.original_pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.current_tk_image = ImageTk.PhotoImage(resized_pil)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.current_tk_image, anchor="nw")
        self.canvas.configure(scrollregion=(0, 0, new_w, new_h))

    def generar_lista_links(self, data_list, title="Noticias Relacionadas"):
        for widget in self.scroll_links.winfo_children():
            widget.destroy()

        # Título dinámico en la lista
        ctk.CTkLabel(self.scroll_links, text=title, font=("Arial", 16, "bold"), text_color="#3498db").pack(pady=5)

        if not data_list:
            ctk.CTkLabel(self.scroll_links, text="No hay noticias.").pack()
            return

        for item in data_list:
            card = ctk.CTkFrame(self.scroll_links)
            card.pack(fill="x", padx=5, pady=5)

            headline = item.get('headline', 'Sin título')
            if len(headline) > 90: headline = headline[:90] + "..."

            ctk.CTkLabel(card, text=headline, font=("Arial", 13, "bold"), anchor="w").pack(fill="x", padx=5,
                                                                                           pady=(5, 0))

            sub_frame = ctk.CTkFrame(card, fg_color="transparent")
            sub_frame.pack(fill="x", padx=5, pady=5)

            tone = item.get('tone', 0)
            emoji_tone = "😐"
            if tone > 0:
                emoji_tone = "🙂 Positivo"
            elif tone < 0:
                emoji_tone = "😡 Negativo"

            ctk.CTkLabel(sub_frame, text=f"📅 {item.get('date', '')} | {emoji_tone}", text_color="gray",
                         font=("Arial", 11)).pack(side="left")

            url = item.get('url', '')
            if url:
                btn = ctk.CTkButton(sub_frame, text="Leer 🔗", height=20, width=60,
                                    command=lambda u=url: webbrowser.open(u))
                btn.pack(side="right")

    def comparar_terminos(self):
        t1 = self.entry_term1.get().lower().strip()
        t2 = self.entry_term2.get().lower().strip()

        if not t1 or not t2: return
        if not self.all_data: return

        count1 = 0
        count2 = 0

        for d in self.all_data:
            words = self._obtener_palabras_limpias(d)
            count1 += words.count(t1)
            count2 += words.count(t2)

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar([t1.upper(), t2.upper()], [count1, count2], color=['#3498db', '#e74c3c'])

        ax.bar_label(bars, padding=3, color='white', fontsize=12, fontweight='bold')
        ax.margins(y=0.2)
        ax.set_title(f"Frecuencia Exacta: {t1.upper()} vs {t2.upper()}", color='white')

        filename = "chart_temp.png"
        plt.savefig(filename, facecolor='#2b2b2b', bbox_inches='tight')
        plt.close()

        if os.path.exists(filename):
            pil_img = Image.open(filename)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(500, 350))
            self.lbl_chart.configure(image=ctk_img, text="")


if __name__ == "__main__":
    app = NewsAnalyzerApp()
    app.mainloop()