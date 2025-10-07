"""
Parser para archivos GDELT (Global Database of Events, Language, and Tone).
Extrae y procesa datos de eventos geopolíticos para análisis de grafos.
"""

import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GDELTEvent:
    """
    Representa un evento GDELT con sus campos principales.
    """
    event_id: str
    event_date: str
    year: str
    actor1_code: str
    actor1_name: str
    actor1_country: str
    actor2_code: str
    actor2_name: str
    actor2_country: str
    location_country: str
    location_state: str
    location_name: str
    latitude: float
    longitude: float
    goldstein_scale: float
    url: str
    
    def get_display_name(self) -> str:
        """Retorna un nombre descriptivo para el evento."""
        parts = []
        if self.actor1_name:
            parts.append(self.actor1_name)
        if self.actor2_name:
            parts.append(self.actor2_name)
        if self.location_name:
            parts.append(f"({self.location_name})")
        return " - ".join(parts) if parts else self.event_id
    
    def get_country_codes(self) -> List[str]:
        """Retorna todos los códigos de país asociados al evento."""
        codes = []
        for code in [self.actor1_country, self.actor2_country, self.location_country]:
            if code and code not in codes:
                codes.append(code)
        return codes


class GDELTParser:
    """
    Parser para archivos GDELT en formato CSV/TSV.
    """
    
    # Índices de columnas basados en el formato GDELT
    COL_EVENT_ID = 0
    COL_EVENT_DATE = 1
    COL_YEAR = 3
    COL_ACTOR1_CODE = 5
    COL_ACTOR1_NAME = 6
    COL_ACTOR2_CODE = 13
    COL_ACTOR2_NAME = 14
    COL_LOCATION_COUNTRY = 15
    COL_LOCATION_STATE = 16
    COL_GOLDSTEIN = 30
    COL_LOCATION_NAME = 39
    COL_LOCATION_COUNTRY_CODE = 40
    COL_LATITUDE = 43
    COL_LONGITUDE = 44
    COL_URL = 57
    
    def __init__(self, filepath: str, delimiter: str = '\t'):
        """
        Inicializa el parser.
        
        Args:
            filepath: Ruta al archivo GDELT
            delimiter: Delimitador del archivo (default: tabulador)
        """
        self.filepath = filepath
        self.delimiter = delimiter
        self.events: List[GDELTEvent] = []
        self.events_by_country: Dict[str, List[GDELTEvent]] = {}
    
    def parse(self, max_rows: Optional[int] = None) -> int:
        """
        Parsea el archivo GDELT.
        
        Args:
            max_rows: Número máximo de filas a procesar (None = todas)
            
        Returns:
            int: Número de eventos parseados
        """
        self.events = []
        self.events_by_country = {}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self.delimiter)
                
                rows_processed = 0
                for row in reader:
                    if max_rows and rows_processed >= max_rows:
                        break
                    
                    if len(row) < 58:  # Validar que tenga suficientes columnas
                        continue
                    
                    try:
                        event = self._parse_row(row)
                        if event:
                            self.events.append(event)
                            
                            # Indexar por país
                            for country in event.get_country_codes():
                                if country not in self.events_by_country:
                                    self.events_by_country[country] = []
                                self.events_by_country[country].append(event)
                            
                            rows_processed += 1
                    except Exception as e:
                        # Ignorar filas con errores
                        continue
                        
        except Exception as e:
            raise Exception(f"Error al parsear archivo GDELT: {str(e)}")
        
        return len(self.events)
    
    def _parse_row(self, row: List[str]) -> Optional[GDELTEvent]:
        """
        Parsea una fila del CSV en un objeto GDELTEvent.
        
        Args:
            row: Fila del CSV
            
        Returns:
            GDELTEvent o None si la fila es inválida
        """
        try:
            # Extraer coordenadas
            lat = float(row[self.COL_LATITUDE]) if row[self.COL_LATITUDE] else 0.0
            lon = float(row[self.COL_LONGITUDE]) if row[self.COL_LONGITUDE] else 0.0
            
            # Extraer Goldstein scale
            goldstein = float(row[self.COL_GOLDSTEIN]) if row[self.COL_GOLDSTEIN] else 0.0
            
            event = GDELTEvent(
                event_id=row[self.COL_EVENT_ID].strip(),
                event_date=row[self.COL_EVENT_DATE].strip(),
                year=row[self.COL_YEAR].strip(),
                actor1_code=row[self.COL_ACTOR1_CODE].strip(),
                actor1_name=row[self.COL_ACTOR1_NAME].strip(),
                actor1_country=row[self.COL_LOCATION_COUNTRY].strip(),
                actor2_code=row[self.COL_ACTOR2_CODE].strip() if len(row) > self.COL_ACTOR2_CODE else "",
                actor2_name=row[self.COL_ACTOR2_NAME].strip() if len(row) > self.COL_ACTOR2_NAME else "",
                actor2_country=row[self.COL_LOCATION_COUNTRY_CODE].strip() if len(row) > self.COL_LOCATION_COUNTRY_CODE else "",
                location_country=row[self.COL_LOCATION_COUNTRY].strip(),
                location_state=row[self.COL_LOCATION_STATE].strip() if len(row) > self.COL_LOCATION_STATE else "",
                location_name=row[self.COL_LOCATION_NAME].strip() if len(row) > self.COL_LOCATION_NAME else "",
                latitude=lat,
                longitude=lon,
                goldstein_scale=goldstein,
                url=row[self.COL_URL].strip() if len(row) > self.COL_URL else ""
            )
            
            return event
            
        except Exception as e:
            return None
    
    def get_events_by_country(self, country_code: str) -> List[GDELTEvent]:
        """
        Obtiene eventos filtrados por código de país.
        
        Args:
            country_code: Código de país (ej: 'USA', 'CAN')
            
        Returns:
            List[GDELTEvent]: Lista de eventos del país
        """
        return self.events_by_country.get(country_code.upper(), [])
    
    def get_event_by_id(self, event_id: str) -> Optional[GDELTEvent]:
        """
        Busca un evento por su ID único.
        
        Args:
            event_id: ID del evento
            
        Returns:
            GDELTEvent o None si no se encuentra
        """
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
    
    def get_available_countries(self) -> List[Tuple[str, int]]:
        """
        Obtiene la lista de países disponibles con conteo de eventos.
        
        Returns:
            List[Tuple[str, int]]: Lista de tuplas (código_país, cantidad_eventos)
        """
        return [(country, len(events)) 
                for country, events in sorted(self.events_by_country.items())]
    
    def build_graph_edges(self, 
                         country_filter: Optional[str] = None,
                         max_distance: float = 1000.0) -> List[Tuple[str, str, float]]:
        """
        Construye aristas de grafo basadas en proximidad geográfica.
        
        Args:
            country_filter: Filtrar eventos por país (None = todos)
            max_distance: Distancia máxima para crear aristas (km)
            
        Returns:
            List[Tuple[str, str, float]]: Lista de aristas (origen, destino, distancia)
        """
        import math
        
        # Filtrar eventos
        events = self.events
        if country_filter:
            events = self.get_events_by_country(country_filter)
        
        edges = []
        
        # Crear aristas entre eventos cercanos geográficamente
        for i, event1 in enumerate(events):
            if event1.latitude == 0 and event1.longitude == 0:
                continue
                
            for event2 in events[i+1:]:
                if event2.latitude == 0 and event2.longitude == 0:
                    continue
                
                # Calcular distancia haversine (aproximada)
                distance = self._calculate_distance(
                    event1.latitude, event1.longitude,
                    event2.latitude, event2.longitude
                )
                
                if distance <= max_distance:
                    # Crear arista bidireccional
                    edges.append((event1.event_id, event2.event_id, distance))
                    edges.append((event2.event_id, event1.event_id, distance))
        
        return edges
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """
        Calcula la distancia haversine entre dos puntos geográficos.
        
        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto
            
        Returns:
            float: Distancia en kilómetros
        """
        import math
        
        R = 6371  # Radio de la Tierra en km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del dataset parseado.
        
        Returns:
            Dict: Estadísticas del dataset
        """
        return {
            'total_events': len(self.events),
            'countries': len(self.events_by_country),
            'events_with_coordinates': sum(1 for e in self.events 
                                          if e.latitude != 0 or e.longitude != 0),
            'date_range': self._get_date_range()
        }
    
    def _get_date_range(self) -> Tuple[str, str]:
        """Obtiene el rango de fechas del dataset."""
        if not self.events:
            return ("", "")
        
        dates = [e.event_date for e in self.events if e.event_date]
        if not dates:
            return ("", "")
        
        return (min(dates), max(dates))
