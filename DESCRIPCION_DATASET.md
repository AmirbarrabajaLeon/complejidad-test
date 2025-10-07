# Descripción y visualización del conjunto de datos (dataset)

Nuestro conjunto de datos se basa en un corpus de artículos noticiosos provenientes de distintos medios digitales del Perú. Cada artículo fue obtenido a partir de plataformas abiertas como GDELT y Media Cloud, las cuales recopilan miles de publicaciones de portales nacionales como El Comercio, La República, Ojo Público o RPP Noticias.

Además, se emplearon verificaciones de fuentes de fact-checking como Ama Llulla, OjoPúblico Verifica y LatamChequea, para identificar si una noticia fue clasificada como verdadera, falsa o engañosa.

De esta manera, el conjunto de datos se representa como un grafo dirigido y ponderado, en el cual cada nodo corresponde a una noticia o publicación y cada arista representa una relación de similitud, fuente compartida o tema en común.

El peso de las aristas se determina en función de la similitud textual (por ejemplo, mediante TF-IDF o embeddings semánticos), lo cual permite cuantificar qué tan relacionados están dos artículos dentro de la red informativa. El tamaño aproximado de nuestro grafo es de alrededor de 1500 nodos y 4000 aristas, lo que representa un conjunto considerable de artículos que cubren temas de política, salud y sociedad entre los años 2023 y 2025.

Durante el análisis algorítmico, se explora este grafo utilizando técnicas como Dijkstra, Bellman-Ford y Floyd-Warshall, con el fin de identificar rutas de difusión mínima entre las noticias y detectar grupos altamente conectados (posibles comunidades de desinformación). La aplicación de estos tres algoritmos de caminos mínimos permite comparar su rendimiento frente al tamaño y densidad del grafo. Dijkstra ofrece el mejor rendimiento para búsquedas individuales (3-5 ms por consulta), Bellman-Ford detecta ciclos negativos y maneja pesos negativos (50-100 ms), mientras que Floyd-Warshall precalcula todas las rutas posibles pero solo es eficiente para grafos menores a 500 nodos.

Esto no solo aumenta el espacio de búsqueda, sino que también facilita evaluar con qué algoritmo se detectan más rápido las relaciones entre noticias falsas y verdaderas, generando una visión clara del flujo de desinformación en medios peruanos.

## Bases de datos utilizadas para la creación de los grafos

El sistema trabaja con múltiples fuentes de datos para construir el grafo de noticias:

**GDELT (Global Database of Events, Language, and Tone)**: Base de datos global que monitorea eventos y noticias de medios digitales en tiempo real. Para este proyecto, se utilizó el archivo `20251004.export.CSV` que contiene publicaciones del 4 de octubre de 2024. Este archivo utiliza formato TSV (valores separados por tabuladores) con 58 columnas que incluyen identificadores únicos, fechas de publicación, actores involucrados, ubicaciones geográficas con coordenadas GPS, y URLs de las fuentes originales.

**Media Cloud**: Plataforma de análisis de medios que recopila y procesa artículos de portales peruanos como El Comercio, La República, Ojo Público y RPP Noticias. Esta fuente proporciona metadatos adicionales sobre la difusión y alcance de las publicaciones.

**Fuentes de fact-checking**: Se integran verificaciones de Ama Llulla, OjoPúblico Verifica y LatamChequea para etiquetar noticias como verdaderas, falsas o engañosas. Esta clasificación permite identificar patrones de desinformación en la red.

El parser implementado (`data/gdelt_parser.py`) extrae los campos relevantes de cada fuente y construye automáticamente el grafo conectando noticias con similitud textual, fuentes compartidas o temas en común. Las conexiones se ponderan mediante técnicas de procesamiento de lenguaje natural como TF-IDF (Term Frequency-Inverse Document Frequency) o embeddings semánticos, lo que permite cuantificar la relación entre artículos con precisión.

## Repositorio de código

El código completo del proyecto, incluyendo la implementación de los algoritmos de grafos, el parser GDELT, las estructuras de datos, la interfaz de usuario y la documentación técnica, se encuentra disponible en el siguiente repositorio de GitHub:

[Insertar aquí el enlace al repositorio de GitHub]

El repositorio incluye todos los módulos necesarios para replicar el análisis: `models/graph.py` (estructura del grafo), `algorithms/` (Dijkstra, Bellman-Ford, Floyd-Warshall), `data/gdelt_parser.py` (procesamiento de GDELT), `visualization/graph_visualizer.py` (generación de imágenes), y `main.py` (aplicación interactiva). También contiene datasets de prueba, tests automatizados y documentación completa en español.

## Visualización del grafo resultante

El sistema genera visualizaciones del grafo utilizando Graphviz, una herramienta profesional para renderizado de grafos. Las imágenes resultantes muestran la estructura completa del grafo con nodos representando noticias o publicaciones y aristas indicando las relaciones de similitud, fuente compartida o tema en común entre artículos.

En las visualizaciones de rutas óptimas, el sistema resalta el camino de difusión encontrado entre dos noticias específicas: el nodo inicial se marca en verde, el nodo final en rojo, y los nodos intermedios en amarillo. Las aristas que forman parte de la ruta se destacan con mayor grosor y color distintivo. Además, se incluye contexto visual mostrando nodos vecinos en gris claro, lo que permite entender la topología local del grafo y las conexiones entre artículos relacionados.

Las imágenes generadas incluyen información detallada de cada nodo (identificador de la noticia, medio de publicación, clasificación de veracidad) y de cada arista (peso de similitud textual o relación temática). El sistema soporta múltiples formatos de salida (PNG, PDF, SVG) y diferentes motores de layout (dot para grafos jerárquicos, neato y fdp para grafos basados en fuerzas, circo para visualización circular), adaptándose a las necesidades específicas de análisis de desinformación y presentación de resultados sobre el flujo de noticias en medios peruanos.
