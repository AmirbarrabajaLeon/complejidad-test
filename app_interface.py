import customtkinter as ctk
from PIL import Image, ImageTk  # ImageTk es necesario para el Canvas
import os
import sys
import webbrowser
import matplotlib.pyplot as plt
import tkinter as tk  # Necesario para el Canvas de 2D Scroll

# --- CONFIGURACIÓN DE SEGURIDAD PARA GRAPHVIZ ---
path_graphviz = r"C:\Program Files\Graphviz\bin"
if os.path.exists(path_graphviz):
    os.environ["PATH"] += os.pathsep + path_graphviz
# ------------------------------------------------

from models.graph import Graph
from data.gdelt_parser import GDELTParser
from visualization.graph_visualizer import GraphVisualizer
from algorithms.merge_sort import merge_sort  # Tu algoritmo de ordenamiento

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NewsAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Análisis de Tendencias - TB2 Final")
        self.geometry("1300x850")

        self.all_data = []
        self.current_filtered_data = []
        self.original_pil_image = None  # Para el zoom
        self.current_tk_image = None  # Referencia para evitar garbage collection

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

        # --- PANEL DE ZOOM (OCULTO POR DEFECTO) ---
        # Lo metemos en un frame para mostrarlo/ocultarlo fácil
        self.zoom_panel = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.zoom_panel.grid(row=5, column=0, pady=20, sticky="ew")

        ctk.CTkLabel(self.zoom_panel, text="--- CONTROL DE VISTA ---").pack()
        self.lbl_zoom = ctk.CTkLabel(self.zoom_panel, text="Zoom: 100%", anchor="w")
        self.lbl_zoom.pack(pady=(5, 0))

        self.slider_zoom = ctk.CTkSlider(self.zoom_panel, from_=0.1, to=2.0, number_of_steps=19,
                                         command=self.actualizar_zoom)
        self.slider_zoom.set(1.0)
        self.slider_zoom.pack(pady=5)

        # Ocultamos el panel al inicio (porque iniciamos en otra pestaña)
        self.zoom_panel.grid_remove()
        # ------------------------------------------

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Estado: Esperando...", text_color="gray", wraplength=200)
        self.lbl_status.grid(row=9, column=0, padx=20, pady=20, sticky="s")

        # === PANEL DERECHO (TABS) ===
        # Agregamos 'command' para detectar cambio de pestaña
        self.tabview = ctk.CTkTabview(self, command=self.al_cambiar_pestana)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tab_stats = self.tabview.add("Comparación (Vs)")
        self.tab_links = self.tabview.add("Fuentes y Enlaces")
        self.tab_graph = self.tabview.add("Grafo Temporal")

        # --- SETUP TAB 1: ESTADÍSTICAS ---
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

        # --- SETUP TAB 2: LINKS ---
        self.tab_links.grid_columnconfigure(0, weight=1)
        self.tab_links.grid_rowconfigure(0, weight=1)
        self.scroll_links = ctk.CTkScrollableFrame(self.tab_links, label_text="Noticias Relacionadas")
        self.scroll_links.grid(row=0, column=0, sticky="nsew")

        # --- SETUP TAB 3: GRAFO (CANVAS CON SCROLL 2D) ---
        self.tab_graph.grid_columnconfigure(0, weight=1)
        self.tab_graph.grid_rowconfigure(0, weight=1)

        # Usamos un Canvas de Tkinter normal porque permite scroll X e Y simultáneo
        # Frame contenedor
        self.graph_container = ctk.CTkFrame(self.tab_graph)
        self.graph_container.grid(row=0, column=0, sticky="nsew")
        self.graph_container.grid_rowconfigure(0, weight=1)
        self.graph_container.grid_columnconfigure(0, weight=1)

        # Canvas y Scrollbars
        self.canvas = tk.Canvas(self.graph_container, bg="#2b2b2b", highlightthickness=0)
        self.v_scroll = ctk.CTkScrollbar(self.graph_container, orientation="vertical", command=self.canvas.yview)
        self.h_scroll = ctk.CTkScrollbar(self.graph_container, orientation="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Grid layout para canvas y barras
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # Placeholder text en el canvas
        self.canvas_text = self.canvas.create_text(400, 300, text="Realiza una búsqueda para ver el grafo.",
                                                   fill="white", font=("Arial", 16))

    def al_cambiar_pestana(self):
        """Muestra u oculta los controles de Zoom según la pestaña activa"""
        tab_actual = self.tabview.get()
        if tab_actual == "Grafo Temporal":
            self.zoom_panel.grid()  # Mostrar
        else:
            self.zoom_panel.grid_remove()  # Ocultar

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
            filtered = filtered[:100]
        else:
            filtered = self.all_data[:50]

        self.current_filtered_data = filtered

        if not filtered:
            self.lbl_status.configure(text="No se encontraron resultados.", text_color="orange")
            return

        # ALGORITMO 1: MERGE SORT (Divide y Vencerás)
        # Ordenamos las noticias por fecha para la línea de tiempo
        try:
            filtered = merge_sort(filtered, key_func=lambda x: x['date'])
        except Exception as e:
            print(f"Error sorting: {e}")

        # GENERAR GRAFO (MALLA TEMPORAL)
        temp_graph = Graph()
        temp_graph.load_from_news_dataset(filtered)
        nodes = temp_graph.get_all_nodes()

        WINDOW_SIZE = 3
        for i in range(len(nodes)):
            for j in range(1, WINDOW_SIZE + 1):
                if i + j < len(nodes):
                    weight = round(1.0 / j, 2)
                    temp_graph.add_edge(nodes[i], nodes[i + j], weight=weight)

        try:
            viz = GraphVisualizer(temp_graph)
            output = "grafo_temp"
            # Engine 'dot' es el mejor para líneas de tiempo
            success = viz.visualize_graph(output_file=output, format="png", max_nodes=100, engine='dot')

            if success:
                self.cargar_imagen_memoria(output + ".png")
                self.generar_lista_links()
                self.lbl_status.configure(text=f"Análisis: {len(nodes)} noticias", text_color="white")

                # --- SIN REDIRECCIÓN FORZADA ---
                # El usuario se queda en la pestaña donde estaba (o puede ir manualmente)
            else:
                self.lbl_status.configure(text="Error Graphviz", text_color="red")
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {e}", text_color="red")

    def cargar_imagen_memoria(self, path):
        if os.path.exists(path):
            self.original_pil_image = Image.open(path)
            self.slider_zoom.set(1.0)
            self.actualizar_zoom(1.0)

    def actualizar_zoom(self, value):
        if self.original_pil_image is None: return

        scale = float(value)
        self.lbl_zoom.configure(text=f"Zoom: {int(scale * 100)}%")

        # Calcular tamaño
        orig_w, orig_h = self.original_pil_image.size
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Redimensionar
        resized_pil = self.original_pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Convertir a formato compatible con Tkinter Canvas
        self.current_tk_image = ImageTk.PhotoImage(resized_pil)

        # Actualizar Canvas
        self.canvas.delete("all")  # Borrar anterior
        # Poner imagen en coordenadas 0,0
        self.canvas.create_image(0, 0, image=self.current_tk_image, anchor="nw")

        # Actualizar región de scroll para que las barras funcionen
        self.canvas.configure(scrollregion=(0, 0, new_w, new_h))

    def generar_lista_links(self):
        for widget in self.scroll_links.winfo_children():
            widget.destroy()

        if not self.current_filtered_data:
            ctk.CTkLabel(self.scroll_links, text="No hay noticias.").pack()
            return

        for item in self.current_filtered_data:
            card = ctk.CTkFrame(self.scroll_links)
            card.pack(fill="x", padx=5, pady=5)

            title = item.get('headline', 'Sin título')
            if len(title) > 100: title = title[:100] + "..."

            ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), anchor="w").pack(fill="x", padx=5, pady=(5, 0))

            sub_frame = ctk.CTkFrame(card, fg_color="transparent")
            sub_frame.pack(fill="x", padx=5, pady=5)

            # Tono visual (Texto)
            # tone_val = item.get('tone', 0)
            # tone_text = "🟢 Positivo" if tone_val > 0 else ("🔴 Conflicto" if tone_val < 0 else "🟡 Neutral")

            ctk.CTkLabel(sub_frame, text=f"{item.get('date', '')}", text_color="gray").pack(side="left")

            url = item.get('url', '')
            if url:
                btn = ctk.CTkButton(sub_frame, text="Leer Fuente 🔗", height=24, width=100,
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
            full_text = (d['headline'] + " " + d['content'] + " " + d.get('url', '')).lower()
            if t1 in full_text: count1 += 1
            if t2 in full_text: count2 += 1

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar([t1.upper(), t2.upper()], [count1, count2], color=['#3498db', '#e74c3c'])
        ax.bar_label(bars, padding=3, color='white', fontsize=12, fontweight='bold')
        ax.margins(y=0.2)
        ax.set_title(f"Frecuencia: {t1.upper()} vs {t2.upper()}", color='white')

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