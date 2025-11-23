import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import datetime

@dataclass
class GDELTEvent:
    """
    Representa una noticia/evento extraído de GDELT.
    Adaptado para análisis de tendencias temporales.
    """
    event_id: str
    date_obj: datetime.datetime  # CAMBIO: Guardamos objeto fecha real
    headline: str                # CAMBIO: Usamos esto como título
    url: str
    content: str                 # CAMBIO: Texto para comparar similitud
    
    # Mantenemos coordenadas solo por si acaso, pero no son el foco
    latitude: float = 0.0
    longitude: float = 0.0

    # --- CORRECCIÓN 1: Agregamos el campo tone aquí ---
    tone: int = 0

class GDELTParser:
    """
    Parser adaptado para extraer NARRATIVAS y TENDENCIAS de GDELT.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.events: List[GDELTEvent] = []
    
    def parse(self, max_rows: int = 3000) -> int:
        """
        Parsea el archivo GDELT limitando a max_rows para rendimiento.
        Retorna la cantidad de eventos cargados.
        """
        print(f"📂 Procesando {self.filepath}...")
        self.events = []
        count = 0
        
        try:
            with (open(self.filepath, 'r', encoding='utf-8', errors='ignore') as file):
                # GDELT usa Tabs (\t)
                reader = csv.reader(file, delimiter='\t')
                
                for row in reader:
                    if count >= max_rows:
                        break
                    
                    # Validación básica de longitud
                    if len(row) < 58: continue
                    
                    try:
                        # --- EXTRACCIÓN DE DATOS ---
                        # ID (Col 0)
                        e_id = row[0]
                        
                        # Fecha (Col 1: YYYYMMDD)
                        raw_date = row[1]
                        try:
                            date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d")
                        except:
                            continue # Si no hay fecha válida, saltamos
                            
                        # Título/Actor (Col 6 o Col 16) - Truco para tener un texto legible
                        title = row[6] if row[6] else (row[16] if row[16] else "Evento Internacional")
                        title = title.replace("_", " ").title()

                        # --- NUEVO: DETECCIÓN SIMPLE DE SENTIMIENTO ---
                        # Si usamos la columna real de GDELT es complejo porque varía.
                        # Simularemos sentimiento analizando el título (Algoritmo de Fuerza Bruta en Strings)
                        tone = 0  # Neutral
                        positive_words = [
                            'Peace', 'Treaty', 'Aid', 'Help', 'Support', 'Win', 'Grow',
                            'Agreement', 'Rescue', 'Save', 'Award', 'Success', 'Clear', 'Safe']

                        negative_words = [
                            'War', 'Kill', 'Attack', 'Crisis', 'Death', 'Conflict', 'Shot',
                            'Dead', 'Murder', 'Crash', 'Disaster', 'Fight', 'Fail', 'Injure',
                            'Overdose', 'Arrest', 'Prison'
                        ]

                        title_lower = title.lower()
                        if any(w.lower() in title_lower for w in positive_words):
                            tone = 5  # Positivo
                        elif any(w.lower() in title_lower for w in negative_words):
                            tone = -5  # Negativo
                        # ---------------------------------------------

                        # URL (Col 57)
                        url = row[57]
                        
                        # Creamos el objeto
                        event = GDELTEvent(
                            event_id=e_id,
                            date_obj=date_obj,
                            headline=title,
                            url=url,
                            content=f"{title} - Fuente: {url}",
                            latitude=float(row[43]) if row[43] else 0,
                            longitude=float(row[44]) if row[44] else 0,

                            # --- CORRECCIÓN 2: Guardamos el tono calculado ---
                            tone=tone


                        )

                        self.events.append(event)
                        count += 1
                        
                    except Exception as e:
                        continue # Error en una fila, seguimos
                        
        except Exception as e:
            print(f"❌ Error crítico leyendo archivo: {e}")
            return 0
            
        print(f"✅ Parseados {len(self.events)} eventos exitosamente.")
        return len(self.events)

    def get_data_for_graph(self) -> List[Dict]:
        """
        Convierte los eventos al formato diccionario que necesita models/graph.py
        """
        graph_data = []
        for e in self.events:
            graph_data.append({
                'id': e.event_id,
                'headline': e.headline,
                'date': e.date_obj.strftime("%Y-%m-%d"), # Formato string limpio
                'content': e.content,
                'url': e.url,

                # --- CORRECCIÓN 3: Exportamos el tono al diccionario ---
                'tone': e.tone
            })
        return graph_data