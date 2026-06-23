import tkinter as tk
from tkinter import scrolledtext
import heapq
import threading
import queue
import random                  
import numpy as np
from scipy.optimize import linear_sum_assignment


# Toda la lógica del juego, incluyendo la generación de la tabla Zobrist y la detección de esquinas muertas, se encuentra en esta clase.
class SokobanLogic:
    def __init__(self, mapa):
        self.zobrist_table = {} # Tabla maestra de códigos
        self.cargar_nivel(mapa)

    def cargar_nivel(self, mapa):
        self.mapa_original = mapa 
        self.reiniciar()
        self.generar_tabla_zobrist()

    def reiniciar(self):
        self.walls = set()
        self.goals = set()
        self.boxes = set()
        self.player = (0, 0)
        self.deadlocks = set()
        
        for y, fila in enumerate(self.mapa_original):
            for x, char in enumerate(fila):
                if char == '#': self.walls.add((x, y))
                elif char == '.': self.goals.add((x, y))
                elif char == '$': self.boxes.add((x, y))
                elif char == '@': self.player = (x, y)
                elif char == '*': 
                    self.goals.add((x, y))
                    self.boxes.add((x, y))
                elif char == '+': 
                    self.goals.add((x, y))
                    self.player = (x, y)

        self.calcular_esquinas_muertas()

    def generar_tabla_zobrist(self):
        self.zobrist_table.clear()
        if not self.walls: return
        max_x = max(x for x, y in self.walls) + 1
        max_y = max(y for x, y in self.walls) + 1
        
        # Asignamos un número aleatorio de 64 bits a cada elemento posible en el mapa
        for y in range(max_y):
            for x in range(max_x):
                if (x, y) not in self.walls:
                    self.zobrist_table[('jugador', x, y)] = random.getrandbits(64)
                    self.zobrist_table[('caja', x, y)] = random.getrandbits(64)

    def obtener_hash_inicial(self):
        # Calcula el hashing del primer tablero
        h = self.zobrist_table[('jugador', self.player[0], self.player[1])]
        for cx, cy in self.boxes:
            h ^= self.zobrist_table[('caja', cx, cy)]
        return h

    def calcular_esquinas_muertas(self):
        if not self.walls: return
        max_x = max(x for x, y in self.walls)
        max_y = max(y for x, y in self.walls)

        for y in range(max_y + 1):
            for x in range(max_x + 1):
                if (x, y) in self.walls or (x, y) in self.goals: continue
                pared_arriba = (x, y - 1) in self.walls
                pared_abajo = (x, y + 1) in self.walls
                pared_izq = (x - 1, y) in self.walls
                pared_der = (x + 1, y) in self.walls

                if (pared_arriba and pared_izq) or (pared_arriba and pared_der) or \
                   (pared_abajo and pared_izq) or (pared_abajo and pared_der):
                    self.deadlocks.add((x, y))

    def mover(self, dx, dy):
        x, y = self.player
        nx, ny = x + dx, y + dy
        if (nx, ny) in self.walls: return False
        if (nx, ny) in self.boxes:
            nnx, nny = nx + dx, ny + dy
            if (nnx, nny) in self.walls or (nnx, nny) in self.boxes: return False
            self.boxes.remove((nx, ny))
            self.boxes.add((nnx, nny))
        self.player = (nx, ny)
        return True

    def esta_resuelto(self):
        return self.goals == self.boxes and len(self.boxes) > 0


#Algoritmos utilizando el Zobrist Hashing para optimizar la gestión de estados visitados.
def heuristica(cajas, metas):
    if not cajas or not metas: return 0
    lista_cajas = list(cajas)
    lista_metas = list(metas)
    
    num_elementos = len(lista_cajas)
    matriz_costos = np.zeros((num_elementos, num_elementos))
    
    for i, (cx, cy) in enumerate(lista_cajas):
        for j, (mx, my) in enumerate(lista_metas):
            matriz_costos[i, j] = abs(cx - mx) + abs(cy - my)
            
    row_ind, col_ind = linear_sum_assignment(matriz_costos)
    return int(matriz_costos[row_ind, col_ind].sum())

def resolver_a_star(logic, cola):
    z_table = logic.zobrist_table
    estado_inicial = (logic.player, frozenset(logic.boxes))
    hash_inicial = logic.obtener_hash_inicial()
    
    metas = logic.goals
    paredes = logic.walls
    trampas = logic.deadlocks 
    
    h_inicial = heuristica(estado_inicial[1], metas)
    frontera = []
    id_estado = 0 
    
    # La tupla ahora incluye el Zobrist Hash
    heapq.heappush(frontera, (h_inicial, 0, id_estado, estado_inicial, hash_inicial, []))
    
    # Solo se guardan numeros enteros
    visitados = set([hash_inicial])
    movimientos = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
    paso = 1

    while frontera:
        f, g, current_id, estado_actual, hash_actual, camino = heapq.heappop(frontera)
        jugador, cajas = estado_actual

        log_str = f"Paso {paso} | OPEN={len(frontera)} ; CLOSED={len(visitados)}\n"
        log_str += f"  -> Explorar NODO {current_id} | f(n)={f} [g={g}, h={f-g}]\n"
        cola.put(("LOG", log_str))
        paso += 1

        if cajas == metas: 
            cola.put(("FIN", camino))
            return

        for dx, dy in movimientos:
            nx, ny = jugador[0] + dx, jugador[1] + dy
            if (nx, ny) in paredes: continue
            
            nuevas_cajas = set(cajas)
            nuevo_hash = hash_actual
            
            # 1. Aplicamos XOR para "mover" al jugador en la memoria Zobrist
            nuevo_hash ^= z_table[('jugador', jugador[0], jugador[1])] # Borramos pos vieja
            nuevo_hash ^= z_table[('jugador', nx, ny)]                 # Agregamos pos nueva
            
            if (nx, ny) in nuevas_cajas:
                nnx, nny = nx + dx, ny + dy
                if (nnx, nny) in paredes or (nnx, nny) in nuevas_cajas or (nnx, nny) in trampas: continue
                
                nuevas_cajas.remove((nx, ny))
                nuevas_cajas.add((nnx, nny))
                
                # 2. Aplicamos XOR para "mover" la caja
                nuevo_hash ^= z_table[('caja', nx, ny)]   # Borramos caja vieja
                nuevo_hash ^= z_table[('caja', nnx, nny)] # Agregamos caja nueva
            
            # Verificamos si este número de 64-bits ya existe en el archivo
            if nuevo_hash not in visitados:
                visitados.add(nuevo_hash)
                nuevo_g = g + 1
                id_estado += 1
                nuevo_h = heuristica(nuevas_cajas, metas)
                nuevo_estado = ((nx, ny), frozenset(nuevas_cajas))
                
                heapq.heappush(frontera, (nuevo_g + nuevo_h, nuevo_g, id_estado, nuevo_estado, nuevo_hash, camino + [(dx, dy)]))
                
    cola.put(("FIN", None))

def resolver_gbfs(logic, cola):
    z_table = logic.zobrist_table
    estado_inicial = (logic.player, frozenset(logic.boxes))
    hash_inicial = logic.obtener_hash_inicial()
    
    metas = logic.goals
    paredes = logic.walls
    trampas = logic.deadlocks 
    
    h_inicial = heuristica(estado_inicial[1], metas)
    frontera = []
    id_estado = 0 
    
    heapq.heappush(frontera, (h_inicial, id_estado, estado_inicial, hash_inicial, []))
    visitados = set([hash_inicial])
    movimientos = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
    paso = 1

    while frontera:
        h, current_id, estado_actual, hash_actual, camino = heapq.heappop(frontera)
        jugador, cajas = estado_actual

        log_str = f"Paso {paso} | OPEN={len(frontera)} ; CLOSED={len(visitados)}\n"
        log_str += f"  -> Explorar NODO {current_id} | h(n)={h}\n"
        cola.put(("LOG", log_str))
        paso += 1

        if cajas == metas: 
            cola.put(("FIN", camino))
            return

        for dx, dy in movimientos:
            nx, ny = jugador[0] + dx, jugador[1] + dy
            if (nx, ny) in paredes: continue
            
            nuevas_cajas = set(cajas)
            nuevo_hash = hash_actual
            
            nuevo_hash ^= z_table[('jugador', jugador[0], jugador[1])]
            nuevo_hash ^= z_table[('jugador', nx, ny)]
            
            if (nx, ny) in nuevas_cajas:
                nnx, nny = nx + dx, ny + dy
                if (nnx, nny) in paredes or (nnx, nny) in nuevas_cajas or (nnx, nny) in trampas: continue
                
                nuevas_cajas.remove((nx, ny))
                nuevas_cajas.add((nnx, nny))
                
                nuevo_hash ^= z_table[('caja', nx, ny)]
                nuevo_hash ^= z_table[('caja', nnx, nny)]
            
            if nuevo_hash not in visitados:
                visitados.add(nuevo_hash)
                id_estado += 1
                nuevo_h = heuristica(nuevas_cajas, metas)
                nuevo_estado = ((nx, ny), frozenset(nuevas_cajas))
                
                heapq.heappush(frontera, (nuevo_h, id_estado, nuevo_estado, nuevo_hash, camino + [(dx, dy)]))
                
    cola.put(("FIN", None))


# Interfaz grafica multihilo
class SokobanApp:
    def __init__(self, master, niveles):
        self.master = master
        self.niveles = niveles
        self.nivel_actual = 0
        self.niveles_desbloqueados = len(self.niveles)
        self.animando = False
        
        self.logic = SokobanLogic(self.niveles[self.nivel_actual])
        self.tamano_celda = 50
        self.cola_resultados = queue.Queue()

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        tk.Label(self.right_frame, text="Iteraciones", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.right_frame, width=45, height=25, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.escribir_log("Sistema listo.\n")

        self.frame_niveles = tk.Frame(self.left_frame)
        self.frame_niveles.pack(pady=5)
        self.botones_niveles = []
        for i in range(len(self.niveles)):
            btn = tk.Button(self.frame_niveles, text=f"Nivel {i+1}", width=8, font=("Arial", 10, "bold"),
                            command=lambda idx=i: self.cambiar_nivel(idx))
            btn.pack(side=tk.LEFT, padx=5)
            self.botones_niveles.append(btn)
        
        self.actualizar_ui_niveles()
        
        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack()
        self.ajustar_canvas()

        self.frame_botones = tk.Frame(self.left_frame)
        self.frame_botones.pack(pady=10)

        self.btn_resolver = tk.Button(self.frame_botones, text="A*", command=self.ejecutar_ia, bg="black", fg="white", font=("Arial", 11, "bold"), width=10)
        self.btn_resolver.pack(side=tk.LEFT, padx=5)

        self.btn_gbfs = tk.Button(self.frame_botones, text="GBFS", command=self.ejecutar_gbfs, bg="royalblue", fg="white", font=("Arial", 11, "bold"), width=10)
        self.btn_gbfs.pack(side=tk.LEFT, padx=5)

        self.btn_reiniciar = tk.Button(self.frame_botones, text="Reiniciar Nivel", command=self.reiniciar_juego, bg="#d9534f", fg="white", font=("Arial", 11, "bold"))
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)

        self.master.bind("<Up>", lambda e: self.intentar_movimiento(0, -1))
        self.master.bind("<Down>", lambda e: self.intentar_movimiento(0, 1))
        self.master.bind("<Left>", lambda e: self.intentar_movimiento(-1, 0))
        self.master.bind("<Right>", lambda e: self.intentar_movimiento(1, 0))

        self.dibujar_tablero()

    def escribir_log(self, texto):
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)

    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)

    def cambiar_nivel(self, indice):
        if self.animando: return 
        self.nivel_actual = indice
        self.logic.cargar_nivel(self.niveles[self.nivel_actual])
        self.ajustar_canvas()
        self.actualizar_ui_niveles()
        self.restablecer_botones_ia()
        self.limpiar_log()
        self.escribir_log(f"--- NIVEL {indice + 1} CARGADO ---")
        self.dibujar_tablero()

    def actualizar_ui_niveles(self):
        for i, btn in enumerate(self.botones_niveles):
            if i < self.niveles_desbloqueados:
                color = "lightblue" if i == self.nivel_actual else "lightgray"
                btn.config(state=tk.NORMAL, bg=color)
            else:
                btn.config(state=tk.DISABLED, bg="#444444")

    def ajustar_canvas(self):
        ancho = max(x for x, y in self.logic.walls) + 1
        alto = max(y for x, y in self.logic.walls) + 1
        self.canvas.config(width=ancho * self.tamano_celda, height=alto * self.tamano_celda)

    def intentar_movimiento(self, dx, dy):
        if self.logic.esta_resuelto() or self.animando: return 
        if self.logic.mover(dx, dy):
            self.dibujar_tablero()
            if self.logic.esta_resuelto():
                self.lanzar_victoria()

    def lanzar_victoria(self):
        self.canvas.create_text(
            int(self.canvas['width'])/2, int(self.canvas['height'])/2, 
            text="¡COMPLETADO!", fill="green", font=("Arial", 22, "bold")
        )
        if self.nivel_actual + 1 == self.niveles_desbloqueados and self.niveles_desbloqueados < len(self.niveles):
            self.niveles_desbloqueados += 1
            self.actualizar_ui_niveles()

    def reiniciar_juego(self):
        if self.animando: return
        while not self.cola_resultados.empty():
            self.cola_resultados.get_nowait()
        self.logic.reiniciar()
        self.restablecer_botones_ia()
        self.limpiar_log()
        self.escribir_log("--- NIVEL REINICIADO ---")
        self.dibujar_tablero()

    def restablecer_botones_ia(self):
        self.btn_resolver.config(text="A*", state=tk.NORMAL, bg="black")
        self.btn_gbfs.config(text="GBFS", state=tk.NORMAL, bg="royalblue")

    def ejecutar_ia(self):
        if self.animando: return
        self.preparar_ejecucion("A*")
        hilo = threading.Thread(target=resolver_a_star, args=(self.logic, self.cola_resultados))
        hilo.start()
        self.master.after(100, self.chequear_cola, self.btn_resolver)

    def ejecutar_gbfs(self):
        if self.animando: return
        self.preparar_ejecucion("GBFS")
        hilo = threading.Thread(target=resolver_gbfs, args=(self.logic, self.cola_resultados))
        hilo.start()
        self.master.after(100, self.chequear_cola, self.btn_gbfs)

    def preparar_ejecucion(self, nombre_algoritmo):
        self.limpiar_log()
        self.escribir_log(f"--- INICIANDO BÚSQUEDA: {nombre_algoritmo} ---")
        self.btn_resolver.config(state=tk.DISABLED)
        self.btn_gbfs.config(state=tk.DISABLED)

    def chequear_cola(self, boton_activo):
        texto_lote = ""
        mensajes_procesados = 0
        try:
            while mensajes_procesados < 500: 
                tipo_mensaje, contenido = self.cola_resultados.get_nowait()
                if tipo_mensaje == "LOG":
                    texto_lote += contenido
                elif tipo_mensaje == "FIN":
                    if texto_lote: self.escribir_log(texto_lote.strip())
                    self.procesar_resultado(contenido, boton_activo)
                    return 
                mensajes_procesados += 1
                
            if texto_lote:
                self.escribir_log(texto_lote.strip())
            self.master.after(10, self.chequear_cola, boton_activo)
                    
        except queue.Empty:
            if texto_lote:
                self.escribir_log(texto_lote.strip())
            self.master.after(100, self.chequear_cola, boton_activo)

    def procesar_resultado(self, camino, boton_activo):
        if camino is not None:
            self.escribir_log(f"\n¡OBJETIVO ENCONTRADO EN {len(camino)} PASOS!")
            self.escribir_log("Secuencia de solución:")
            
            # traducir de coordenadas a texto legible
            traduccion = {
                (0, -1): "Arriba",
                (0, 1):  "Abajo",
                (-1, 0): "Izquierda",
                (1, 0):  "Derecha"
            }
            
            
            movimientos_texto = []
            for dx, dy in camino:
                movimientos_texto.append(traduccion.get((dx, dy), "?"))
                
            # Formateamos la lista para que se vea compacta 
            ruta_formateada = " -> ".join(movimientos_texto)
            self.escribir_log(ruta_formateada + "\n")

            # Iniciamos la animación
            boton_activo.config(text="Animando...")
            self.animando = True
            self.animar_solucion(camino, boton_activo)
        else:
            self.escribir_log("\nERROR: No se encontró solución posible.")
            boton_activo.config(text="Sin solución", bg="red")

    def animar_solucion(self, camino, boton_activo):
        if not camino:
            boton_activo.config(text="Terminado", bg="green")
            self.animando = False
            return
            
        dx, dy = camino.pop(0)
        self.logic.mover(dx, dy)
        self.dibujar_tablero()
        
        if self.logic.esta_resuelto():
            self.lanzar_victoria()
            self.animando = False
            boton_activo.config(text="Terminado", bg="green")
            return

        self.master.after(200, lambda: self.animar_solucion(camino, boton_activo))

    def dibujar_tablero(self):
        self.canvas.delete("all")
        for x, y in self.logic.goals: self._dibujar_celda(x, y, "lightgreen", oval=True)
        for x, y in self.logic.walls: self._dibujar_celda(x, y, "gray")
        for x, y in self.logic.boxes:
            color = "orange" if (x, y) in self.logic.goals else "saddlebrown"
            self._dibujar_celda(x, y, color)
        px, py = self.logic.player
        self._dibujar_celda(px, py, "blue", oval=True)

    def _dibujar_celda(self, x, y, color, oval=False):
        x1, y1 = x * self.tamano_celda, y * self.tamano_celda
        x2, y2 = x1 + self.tamano_celda, y1 + self.tamano_celda
        if oval:
            self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color, outline="black")
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

# Niveles de prueba y ejecución de la aplicación
if __name__ == "__main__":
    LISTA_DE_NIVELES = [
        [ # NIVEL 1
            "  ##### ",
            "  #   # ",
            "  #$  # ",
            "###  $###",
            "#  .  . #",
            "### #####",
            "  #@#   ",
            "  ###   "
        ],
        [ # NIVEL 2
            "##########",
            "#   #    #",
            "# .    . #",
            "#  $$$$  #",
            "# .    . #",
            "####  ####",
            "   #@#    ",
            "   ###    "
        ],
        [ # NIVEL 3
            "  ##### ",
            "###   # ",
            "#.@$  # ",
            "### $.# ",
            "#.##$ # ",
            "# # . ##",
            "#$ *$$.#",
            "#   .  #",
            "########"
        ]
    ]
    
    raiz = tk.Tk()
    raiz.title("Sokoban")
    app = SokobanApp(raiz, LISTA_DE_NIVELES)
    raiz.mainloop()