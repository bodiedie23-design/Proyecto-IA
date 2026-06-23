import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from collections import deque

class FrozenLakeApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Búsqueda No Informada - Frozen Lake")
        
        # 4 Niveles con dificultad progresiva
        # S: Inicio, F: Hielo Seguro, H: Hoyo, G: Meta
        self.niveles = [
            [   # Nivel 1 (4x4)
                "SFFF",
                "FHFH",
                "FFFH",
                "HFFG"
            ],
            [   # Nivel 2 (5x5)
                "SFFFF",
                "FHFFF",
                "FFHFF",
                "HFFHF",
                "FFFFG"
            ],
            [   # Nivel 3 (6x6)
                "SFFFFF",
                "FHFFHF",
                "FFHFFF",
                "HFFFFH",
                "FFFFHF",
                "FFFFFG"
            ],
            [   # Nivel 4 (8x8)
                "SFFFFFFF",
                "FFFFFFFF",
                "FFFHFFFF",
                "FFFFHFFF",
                "FFFHFFFF",
                "FHFFHFFF",
                "FHFFFFHF",
                "FFFHFFFG"
            ]
        ]
        
        self.nivel_actual = 0
        self.tamano_celda = 50
        self.animando = False
        
        # Contenedor Principal (Layout dividido en Izquierda y Derecha)
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Panel de Logs / Iteraciones (Derecha)
        tk.Label(self.right_frame, text="Iteraciones del Algoritmo", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.right_frame, width=45, height=25, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Controles de Selección de Nivel (Izquierda)
        self.frame_niveles = tk.Frame(self.left_frame)
        self.frame_niveles.pack(pady=5)
        
        self.botones_niveles = []
        for i in range(len(self.niveles)):
            btn = tk.Button(self.frame_niveles, text=f"Nivel {i+1}", width=8, font=("Arial", 10, "bold"),
                            command=lambda idx=i: self.cambiar_nivel(idx))
            btn.pack(side=tk.LEFT, padx=3)
            self.botones_niveles.append(btn)
            
        # Canvas para el tablero de juego
        self.canvas = tk.Canvas(self.left_frame, bg="white", borderwidth=1, relief="solid")
        self.canvas.pack(pady=10)
        
        # Controles de Algoritmo y Ejecución
        self.frame_botones = tk.Frame(self.left_frame)
        self.frame_botones.pack(pady=5)
        
        self.btn_bfs = tk.Button(self.frame_botones, text="Ejecutar BFS", command=self.ejecutar_bfs, bg="lightblue", font=("Arial", 11, "bold"), width=12)
        self.btn_bfs.pack(side=tk.LEFT, padx=5)
        
        self.btn_dfs = tk.Button(self.frame_botones, text="Ejecutar DFS", command=self.ejecutar_dfs, bg="lightgreen", font=("Arial", 11, "bold"), width=12)
        self.btn_dfs.pack(side=tk.LEFT, padx=5)
        
        self.btn_reiniciar = tk.Button(self.frame_botones, text="Reiniciar", command=self.reiniciar_nivel, bg="#d9534f", fg="white", font=("Arial", 11, "bold"), width=10)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)

        tk.Label(self.left_frame, text="Prioridad de exploración: Arriba, Abajo, Izquierda, Derecha", font=("Arial", 10, "italic"), fg="gray").pack(pady=10)
        
        self.cargar_configuracion_nivel()

    def escribir_log(self, texto):
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)

    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)

    def cargar_configuracion_nivel(self):
        self.mapa = self.niveles[self.nivel_actual]
        self.filas = len(self.mapa)
        self.cols = len(self.mapa[0])
        
        # Buscar posiciones de inicio (S) y meta (G)
        self.inicio = (0, 0)
        self.meta = (0, 0)
        for r in range(self.filas):
            for c in range(self.cols):
                if self.mapa[r][c] == 'S': self.inicio = (r, c)
                if self.mapa[r][c] == 'G': self.meta = (r, c)
                
        # Ajustar dimensiones del Canvas dinámicamente
        self.canvas.config(width=self.cols * self.tamano_celda, height=self.filas * self.tamano_celda)
        self.actualizar_ui_botones_nivel()
        self.limpiar_log()
        self.escribir_log(f"--- FROZEN LAKE: NIVEL {self.nivel_actual + 1} CARGADO ---")
        self.escribir_log(f"Dimensiones: {self.filas}x{self.cols}")
        self.dibujar_tablero()

    def cambiar_nivel(self, indice):
        if self.animando: return
        self.nivel_actual = indice
        self.cargar_configuracion_nivel()

    def actualizar_ui_botones_nivel(self):
        for i, btn in enumerate(self.botones_niveles):
            color = "royalblue" if i == self.nivel_actual else "lightgray"
            texto_color = "white" if i == self.nivel_actual else "black"
            btn.config(bg=color, fg=texto_color)

    def reiniciar_nivel(self):
        if self.animando: return
        self.cargar_configuracion_nivel()

    def dibujar_tablero(self, camino=None, celdas_visitadas=None):
        self.canvas.delete("all")
        colores = {'S': 'lightgreen', 'F': '#e6f7ff', 'H': '#141414', 'G': '#ff4d4f'}
        
        set_camino = set(camino) if camino else set()
        set_visitados = set(celdas_visitadas) if celdas_visitadas else set()
        
        for r in range(self.filas):
            for c in range(self.cols):
                x1, y1 = c * self.tamano_celda, r * self.tamano_celda
                x2, y2 = x1 + self.tamano_celda, y1 + self.tamano_celda
                
                tipo = self.mapa[r][c]
                bg_color = colores[tipo]
                
                if tipo == 'S':
                    texto = 'I'
                elif tipo == 'G':
                    texto = 'F'
                else:
                    texto = ''
                
                fg_color = "black"
                
                # Resaltar si pertenece al camino de la solución o fue visitado
                if (r, c) in set_camino and tipo not in ['S', 'G']:
                    bg_color = "#ff9c6e"  # Naranja para la ruta final
                    texto = "•"
                elif (r, c) in set_visitados and tipo not in ['S', 'G', 'H']:
                    bg_color = "#bae7ff"  # Azul claro para nodos explorados en el proceso
                
                if tipo == 'H': fg_color = "white"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="#d9d9d9")
                self.canvas.create_text(x1 + self.tamano_celda/2, y1 + self.tamano_celda/2, 
                                        text=texto, font=("Arial", 12, "bold"), fill=fg_color)

    def obtener_vecinos(self, r, c):
        vecinos = []
        # Movimientos válidos: Arriba, Abajo, Izquierda, Derecha
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in movimientos:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.filas and 0 <= nc < self.cols:
                if self.mapa[nr][nc] != 'H':  # No se puede caminar sobre hoyos
                    vecinos.append((nr, nc))
        return vecinos

    def animar_solucion(self, camino, visitados_secuencia):
        self.animando = True
        self.btn_bfs.config(state=tk.DISABLED)
        self.btn_dfs.config(state=tk.DISABLED)
        self.btn_reiniciar.config(state=tk.DISABLED)
        
        # Fase 1: Animar la exploración del algoritmo (Nodos visitados)
        def mostrar_exploracion(idx):
            if idx <= len(visitados_secuencia):
                self.dibujar_tablero(camino=None, celdas_visitadas=visitados_secuencia[:idx])
                self.master.after(50, mostrar_exploracion, idx + 1)
            else:
                # Fase 2: Animar la ruta final encontrada
                mostrar_ruta(0)

        # Fase 2: Trazar el camino directo hacia la meta
        def mostrar_ruta(idx):
            if idx <= len(camino):
                self.dibujar_tablero(camino=camino[:idx], celdas_visitadas=visitados_secuencia)
                self.master.after(100, mostrar_ruta, idx + 1)
            else:
                self.animando = False
                self.btn_bfs.config(state=tk.NORMAL)
                self.btn_dfs.config(state=tk.NORMAL)
                self.btn_reiniciar.config(state=tk.NORMAL)
                messagebox.showinfo("Éxito", f"¡Meta alcanzada en {len(camino) - 1} pasos!")

        mostrar_exploracion(0)

    def ejecutar_bfs(self):
        self.limpiar_log()
        self.btn_bfs.config(state=tk.DISABLED)
        self.btn_dfs.config(state=tk.DISABLED)
        self.escribir_log("--- INICIANDO BÚSQUEDA: BFS (En Anchura) ---")
        
        frontera = deque([[self.inicio]])
        visitados = set([self.inicio])
        historial_exploracion = [self.inicio] # Para la animación secuencial
        
        paso = 1
        encontrado = False
        
        while frontera:
            camino = frontera.popleft()
            actual = camino[-1]
            
            self.escribir_log(f"Paso {paso} | OPEN={len(frontera)} ; CLOSED={len(visitados)}")
            self.escribir_log(f"  -> Explorando Nodo: {actual}")
            paso += 1
            
            if actual == self.meta:
                encontrado = True
                self.escribir_log(f"\n¡OBJETIVO ENCONTRADO EN {len(camino)-1} PASOS!")
                self.animar_solucion(camino, historial_exploracion)
                return
                
            for vecino in self.obtener_vecinos(actual[0], actual[1]):
                if vecino not in visitados:
                    visitados.add(vecino)
                    historial_exploracion.append(vecino)
                    frontera.append(camino + [vecino])
                    
        if not encontrado:
            self.escribir_log("\nERROR: No existe un camino posible hacia la meta.")
            messagebox.showwarning("Sin solución", "El algoritmo determinó que la meta es inaccesible.")

    def ejecutar_dfs(self):
        self.limpiar_log()
        self.btn_bfs.config(state=tk.DISABLED)
        self.btn_dfs.config(state=tk.DISABLED)
        self.escribir_log("--- INICIANDO BÚSQUEDA: DFS (En Profundidad) ---")
        
        frontera = [[self.inicio]] # Usado como Pila (Stack)
        visitados = set([self.inicio])
        historial_exploracion = [self.inicio]
        
        paso = 1
        encontrado = False
        
        while frontera:
            camino = frontera.pop() # LIFO
            actual = camino[-1]
            
            self.escribir_log(f"Paso {paso} | OPEN={len(frontera)} ; CLOSED={len(visitados)}")
            self.escribir_log(f"  -> Explorando Nodo: {actual}")
            paso += 1
            
            if actual == self.meta:
                encontrado = True
                self.escribir_log(f"\n¡OBJETIVO ENCONTRADO EN {len(camino)-1} PASOS!")
                self.animar_solucion(camino, historial_exploracion)
                return
                
            for vecino in self.obtener_vecinos(actual[0], actual[1]):
                if vecino not in visitados:
                    visitados.add(vecino)
                    historial_exploracion.append(vecino)
                    frontera.append(camino + [vecino])
                    
        if not encontrado:
            self.escribir_log("\nERROR: No existe un camino posible hacia la meta.")
            messagebox.showwarning("Sin solución", "El algoritmo determinó que la meta es inaccesible.")

if __name__ == "__main__":
    raiz = tk.Tk()
    app = FrozenLakeApp(raiz)
    raiz.mainloop()