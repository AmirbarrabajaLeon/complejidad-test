import customtkinter as ctk
from PIL import Image
import os
import sys
import webbrowser  # Para abrir links
import matplotlib.pyplot as plt  # Para graficos estadisticos


# --- CONFIGURACIÓN DE SEGURIDAD PARA GRAPHVIZ ---
# Ajusta esta ruta si tu instalación es diferente
path_graphviz = r"C:\Program Files\Graphviz\bin"
if os.path.exists(path_graphviz):
    os.environ["PATH"] += os.pathsep + path_graphviz
# ------------------------------------------------

from models.graph import Graph
from data.gdelt_parser import GDELTParser
from visualization.graph_visualizer import GraphVisualizer
# ... otros imports ...
from algorithms.merge_sort import merge_sort # <--- AGREGAR ESTO

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NewsAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Análisis de Tendencias - TB2 Final")
        self.geometry("1300x850")

        self.all_data = []
        self.current_filtered_data = []  # Guardamos lo ultimo buscado para los links

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === PANEL IZQUIERDO (CONTROLES) ===
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="PANEL DE CONTROL", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_load = ctk.CTkButton(self.sidebar, text="1. Cargar Dataset", command=self.cargar_datos)
        self.btn_load.grid(row=1, column=0, padx=20, pady=10)

        self.lbl_search = ctk.CTkLabel(self.sidebar, text="Búsqueda Principal:", anchor="w")
        self.lbl_search.grid(row=2, column=0, padx=20, pady=(20, 0))
        self.entry_search = ctk.CTkEntry(self.sidebar, placeholder_text="Ej: Peru")
        self.entry_search.grid(row=3, column=0, padx=20, pady=5)

        self.btn_analyze = ctk.CTkButton(self.sidebar, text="2. Analizar", fg_color="green",
                                         command=self.ejecutar_analisis)
        self.btn_analyze.grid(row=4, column=0, padx=20, pady=20)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Estado: Esperando...", text_color="gray", wraplength=200)
        self.lbl_status.grid(row=9, column=0, padx=20, pady=20, sticky="s")

        # === PANEL DERECHO (TABS) ===
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # ORDEN DE PESTAÑAS MODIFICADO:
        # 1. Comparación (Lo principal)
        # 2. Fuentes (Resultados de búsqueda)
        # 3. Grafo (Visualización extra)
        self.tab_stats = self.tabview.add("Comparación (Vs)")
        self.tab_links = self.tabview.add("Fuentes y Enlaces")
        self.tab_graph = self.tabview.add("Grafo Temporal")

        # --- SETUP TAB 1: ESTADÍSTICAS (VS) ---
        self.tab_stats.grid_columnconfigure(0, weight=1)
        self.tab_stats.grid_rowconfigure(1, weight=1)

        self.frame_vs = ctk.CTkFrame(self.tab_stats)
        self.frame_vs.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.entry_term1 = ctk.CTkEntry(self.frame_vs, placeholder_text="Término A (ej: Biden)")
        self.entry_term1.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkLabel(self.frame_vs, text="VS").pack(side="left", padx=5)

        self.entry_term2 = ctk.CTkEntry(self.frame_vs, placeholder_text="Término B (ej: Trump)")
        self.entry_term2.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(self.frame_vs, text="Comparar", command=self.comparar_terminos).pack(side="left", padx=5)

        self.lbl_chart = ctk.CTkLabel(self.tab_stats, text="")
        self.lbl_chart.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # --- SETUP TAB 2: LINKS ---
        self.tab_links.grid_columnconfigure(0, weight=1)
        self.tab_links.grid_rowconfigure(0, weight=1)
        self.scroll_links = ctk.CTkScrollableFrame(self.tab_links, label_text="Noticias Relacionadas")
        self.scroll_links.grid(row=0, column=0, sticky="nsew")

        # --- SETUP TAB 3: GRAFO ---
        self.tab_graph.grid_columnconfigure(0, weight=1)
        self.tab_graph.grid_rowconfigure(0, weight=1)
        # Orientation horizontal para scroll infinito lateral
        self.scroll_frame_graph = ctk.CTkScrollableFrame(self.tab_graph, orientation="horizontal",
                                                         label_text="Línea de Tiempo")
        self.scroll_frame_graph.grid(row=0, column=0, sticky="nsew")
        self.image_label = ctk.CTkLabel(self.scroll_frame_graph, text="Realiza una búsqueda para ver el grafo.")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)

    def cargar_datos(self):
        self.lbl_status.configure(text="Cargando CSV...", text_color="yellow")
        self.update()
        try:
            # Asegúrate que la ruta sea correcta
            filepath = os.path.join("data", "20251004.export.CSV")
            if not os.path.exists(filepath):
                self.lbl_status.configure(text="ERROR: Falta CSV en carpeta data", text_color="red")
                return

            parser = GDELTParser(filepath)
            # Carga 5000 filas para tener bastantes datos
            parser.parse(max_rows=5000)
            self.all_data = parser.get_data_for_graph()

            self.lbl_status.configure(text=f"Dataset OK: {len(self.all_data)} noticias", text_color="green")
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {str(e)}", text_color="red")

    def ejecutar_analisis(self):
        """Función principal al buscar"""
        if not self.all_data:
            self.lbl_status.configure(text="¡Carga datos primero!", text_color="orange")
            return

        keyword = self.entry_search.get().lower().strip()
        self.lbl_status.configure(text="Procesando...", text_color="yellow")
        self.update()

        # 1. FILTRADO INTELIGENTE
        filtered = []
        if keyword:
            # Buscar en Titular o Contenido
            filtered = [d for d in self.all_data if keyword in d['headline'].lower() or keyword in d['content'].lower()]
            # Top 100
            filtered = filtered[:100]
        else:
            filtered = self.all_data[:50]

        self.current_filtered_data = filtered

        if not filtered:
            self.lbl_status.configure(text="No se encontraron resultados.", text_color="orange")
            return

        print("Aplicando Merge Sort...")
        filtered = merge_sort(filtered, key_func=lambda x: x['date'])

        # 2. GENERAR GRAFO (Backend)
        temp_graph = Graph()
        temp_graph.load_from_news_dataset(filtered)
        nodes = temp_graph.get_all_nodes()
        for i in range(len(nodes) - 1):
            temp_graph.add_edge(nodes[i], nodes[i + 1], weight=1.0)

        # 3. DIBUJAR GRAFO (Frontend)
        try:
            viz = GraphVisualizer(temp_graph)
            output = "grafo_temp"
            success = viz.visualize_graph(output_file=output, format="png", max_nodes=100, engine='dot')

            if success:
                self.mostrar_imagen_grafo(output + ".png")
                self.generar_lista_links()
                self.lbl_status.configure(text=f"Análisis: {len(nodes)} noticias", text_color="white")

                # CAMBIO SOLICITADO: Ir directo a la pestaña Fuentes
                self.tabview.set("Fuentes y Enlaces")
            else:
                self.lbl_status.configure(text="Error Graphviz", text_color="red")
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {e}", text_color="red")

    def mostrar_imagen_grafo(self, path):
        if os.path.exists(path):
            pil_img = Image.open(path)
            w, h = pil_img.size

            # Zoom/Altura fija para scroll horizontal
            viewport_height = 100

            aspect = w / h
            new_w = int(viewport_height * aspect)

            pil_img = pil_img.resize((new_w, viewport_height), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, viewport_height))
            self.image_label.configure(image=ctk_img, text="")

    def generar_lista_links(self):
        """Rellena la Pestaña Fuentes"""
        # Limpiar lo anterior
        for widget in self.scroll_links.winfo_children():
            widget.destroy()

        if not self.current_filtered_data:
            ctk.CTkLabel(self.scroll_links, text="No hay noticias para mostrar.").pack()
            return

        for item in self.current_filtered_data:
            card = ctk.CTkFrame(self.scroll_links)
            card.pack(fill="x", padx=5, pady=5)

            title = item.get('headline', 'Sin título')
            # Recortar títulos muy largos
            if len(title) > 100: title = title[:100] + "..."

            ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), anchor="w").pack(fill="x", padx=5, pady=(5, 0))

            sub_frame = ctk.CTkFrame(card, fg_color="transparent")
            sub_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(sub_frame, text=item.get('date', ''), text_color="gray").pack(side="left")

            url = item.get('url', '')
            if url:
                btn = ctk.CTkButton(sub_frame, text="Leer Fuente 🔗", height=24, width=100,
                                    command=lambda u=url: webbrowser.open(u))
                btn.pack(side="right")

    def comparar_terminos(self):
        """Lógica de Comparación (Estadísticas)"""
        t1 = self.entry_term1.get().lower().strip()
        t2 = self.entry_term2.get().lower().strip()

        if not t1 or not t2:
            print("⚠️ Faltan términos")
            return

        if not self.all_data:
            print("⚠️ Carga datos primero")
            return

        # Búsqueda profunda en todo el texto
        count1 = 0
        count2 = 0

        for d in self.all_data:
            full_text = (d['headline'] + " " + d['content'] + " " + d.get('url', '')).lower()
            if t1 in full_text: count1 += 1
            if t2 in full_text: count2 += 1

        # Generar gráfico
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4))

        bars = ax.bar([t1.upper(), t2.upper()], [count1, count2], color=['#3498db', '#e74c3c'])

        ax.margins(y=0.2)  # Agrega 20% de aire arriba

        ax.bar_label(bars, padding=3, color='white', fontsize=12, fontweight='bold')


        ax.set_title(f"Frecuencia: {t1.upper()} vs {t2.upper()}", color='white')

        # Ajuste si ambos son 0
        if count1 == 0 and count2 == 0:
            ax.set_ylim(0, 1)
            ax.text(0.5, 0.5, "Sin coincidencias", ha='center', va='center', color='gray')

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