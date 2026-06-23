# Proyecto Final - Algoritmos de Búsqueda

Este es el proyecto final de la materia de Inteligencia Artificial. Consiste en una aplicación de escritorio nativa e interactiva que permite visualizar y ejecutar distintos algoritmos de búsqueda aplicados a cuatro problemas y entornos clásicos.

# Tecnologías Utilizadas

- Lenguaje Principal: [Python 3](https://www.python.org/) 
- Librería de Interfaz Gráfica: [Tkinter](https://docs.python.org/3/library/tkinter.html) (Manejo de ventanas, canvas interactivos y menús de forma nativa).
- Librerías Científicas: [NumPy](https://numpy.org/) y [SciPy](https://scipy.org/) (Utilizadas específicamente para la optimización de heurísticas y resolución de matrices en el entorno de Sokoban).

# Entornos y Algoritmos Implementados

La interfaz centraliza cuatro módulos independientes, cada uno atacando un tipo de búsqueda específico:

1. Búsqueda No Informada (Frozen Lake): Implementación de BFS (Búsqueda en Anchura) y DFS (Búsqueda en Profundidad).
   - Detección de caminos seguros evitando obstáculos (hoyos) en mallas de tamaño variable.

2. Búsqueda Informada (Sokoban): Implementación de A y GBFS (Greedy Best-First Search).
   - Optimización de memoria para el control de estados visitados.

3. Búsqueda Local (8 Reinas): Implementación de Hill Climbing y Recocido Simulado.
   - Resolución de conflictos de estado único (0 ataques en tablero).

4. Búsqueda Adversaria (Gato Invencible): Implementación de Minimax tradicional y Minimax con Poda Alfa-Beta.
   - Árbol de decisiones exhaustivo para garantizar que la IA nunca pierda.

# Requisitos Previos

Para ejecutar el proyecto sin problemas, necesitas tener instalado lo siguiente:

- Python: Versión 3.8 o superior.
- Dependencias Externas: Es estrictamente necesario instalar NumPy y SciPy para el correcto funcionamiento del algoritmo de asignación en Sokoban. Puedes instalarlos ejecutando el siguiente comando en tu terminal:

*pip install numpy scipy*

# Instrucciones de Ejecución
A diferencia de los entornos web, este proyecto no requiere levantar servidores locales.

Asegúrate de que los cinco archivos (main.py, Sokoban.py, frozenlake.py, 8 reinas.py, Gato.py) estén exactamente en la misma carpeta.

Abre una terminal o consola de comandos en esa ubicación.

Ejecuta el archivo principal:

python main.py

📁 Estructura principal del proyecto

PROYECTO/

├── 📄 8 reinas.py       <-- Lógica, heurísticas e interfaz del problema de las 8 Reinas.

├── 📄 frozenlake.py     <-- Lógica, mallas dinámicas e interfaz del Frozen Lake.

├── 📄 Gato.py           <-- Motor minimax, poda alfa-beta e interfaz interactiva del Gato.

├── 📄 main.py           <-- Menú principal e integrador de módulos (Tkinter).

├── 📄 Sokoban.py        <-- Lógica avanzada e interfaz del Sokoban.

└── 📄 README.md         <-- Documentación actual.

👤 Autores y Créditos
Alumnos:

- Díaz Presas Angel Aarón
- López Cano Diego
- Sandoval Espinoza Moisés

Institución: 
Instituto Politécnico Nacional.
Escuela Superior de Cómputo.

Asignatura: 
Inteligencia Artificial

Grupo: 6CM1

Equipo 10