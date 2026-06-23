import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import math

class GatoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Búsqueda Adversaria - Gato Invencible")
        
        self.jugador = 'X'
        self.ia = 'O'
        self.tablero = [' ' for _ in range(9)]
        self.juego_activo = True
        self.tamano_celda = 100
        
        # Variables para métricas
        self.nodos_evaluados = 0
        
        # Contenedor Principal
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Panel de Logs
        tk.Label(self.right_frame, text="Iteraciones y Nodos (IA)", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.right_frame, width=45, height=25, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Nivel N/A
        self.frame_niveles = tk.Frame(self.left_frame)
        self.frame_niveles.pack(pady=5)
        tk.Label(self.frame_niveles, text="Niveles: N/A (Tablero fijo 3x3)", font=("Arial", 10, "italic"), fg="gray").pack()
        
        # Selección de Algoritmo
        self.frame_algoritmos = tk.Frame(self.left_frame)
        self.frame_algoritmos.pack(pady=10)
        tk.Label(self.frame_algoritmos, text="Selecciona el Algoritmo de la IA:", font=("Arial", 10, "bold")).pack()
        
        self.algoritmo_var = tk.StringVar(value="alfabeta")
        tk.Radiobutton(self.frame_algoritmos, text="Minimax Tradicional", variable=self.algoritmo_var, value="minimax", font=("Arial", 10)).pack(anchor="w")
        tk.Radiobutton(self.frame_algoritmos, text="Minimax con Poda Alfa-Beta", variable=self.algoritmo_var, value="alfabeta", font=("Arial", 10)).pack(anchor="w")
        
        # Canvas del Tablero
        self.canvas = tk.Canvas(self.left_frame, width=300, height=300, bg="white", borderwidth=2, relief="groove")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.click_jugador)
        
        # Botón Reiniciar
        self.btn_reiniciar = tk.Button(self.left_frame, text="Reiniciar Partida", command=self.reiniciar, bg="#d9534f", fg="white", font=("Arial", 11, "bold"), width=15)
        self.btn_reiniciar.pack(pady=5)
        
        self.escribir_log("--- SISTEMA LISTO ---")
        self.escribir_log("Tú juegas con 'X', la IA juega con 'O'.\n¡Intenta ganarle!")
        self.dibujar_tablero_lineas()

    def escribir_log(self, texto):
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)

    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)

    def dibujar_tablero_lineas(self):
        self.canvas.delete("all")
        # Líneas verticales
        self.canvas.create_line(100, 0, 100, 300, width=4, fill="black")
        self.canvas.create_line(200, 0, 200, 300, width=4, fill="black")
        # Líneas horizontales
        self.canvas.create_line(0, 100, 300, 100, width=4, fill="black")
        self.canvas.create_line(0, 200, 300, 200, width=4, fill="black")
        
        # Dibujar X y O
        for i in range(9):
            if self.tablero[i] != ' ':
                fila = i // 3
                col = i % 3
                x_centro = col * 100 + 50
                y_centro = fila * 100 + 50
                
                if self.tablero[i] == 'X':
                    self.canvas.create_text(x_centro, y_centro, text="X", font=("Arial", 60, "bold"), fill="blue")
                elif self.tablero[i] == 'O':
                    self.canvas.create_text(x_centro, y_centro, text="O", font=("Arial", 60, "bold"), fill="red")

    def click_jugador(self, event):
        if not self.juego_activo: return
        
        col = event.x // 100
        fila = event.y // 100
        indice = fila * 3 + col
        
        if self.tablero[indice] == ' ':
            self.tablero[indice] = self.jugador
            self.dibujar_tablero_lineas()
            
            if self.verificar_estado_juego():
                return
                
            # Turno de la IA con un pequeño retraso para que se sienta fluido
            self.master.after(100, self.turno_ia)

    def turno_ia(self):
        self.escribir_log(f"\n--- TURNO DE LA IA ({self.algoritmo_var.get().upper()}) ---")
        self.nodos_evaluados = 0
        mejor_puntaje = -math.inf
        mejor_movimiento = None
        
        for i in range(9):
            if self.tablero[i] == ' ':
                self.tablero[i] = self.ia
                
                if self.algoritmo_var.get() == "minimax":
                    puntaje = self.minimax(self.tablero, 0, False)
                else:
                    puntaje = self.alfa_beta(self.tablero, 0, -math.inf, math.inf, False)
                    
                self.tablero[i] = ' '
                
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_movimiento = i
                    
        self.tablero[mejor_movimiento] = self.ia
        self.dibujar_tablero_lineas()
        
        self.escribir_log(f"-> Nodos/Estados evaluados: {self.nodos_evaluados}")
        self.escribir_log(f"-> Movimiento elegido en índice: {mejor_movimiento}")
        
        self.verificar_estado_juego()

    def minimax(self, tablero, profundidad, es_maximizador):
        self.nodos_evaluados += 1
        puntaje = self.evaluar_tablero()
        
        if puntaje == 10: return puntaje - profundidad
        if puntaje == -10: return puntaje + profundidad
        if ' ' not in tablero: return 0
        
        if es_maximizador:
            max_eval = -math.inf
            for i in range(9):
                if tablero[i] == ' ':
                    tablero[i] = self.ia
                    eval_actual = self.minimax(tablero, profundidad + 1, False)
                    tablero[i] = ' '
                    max_eval = max(max_eval, eval_actual)
            return max_eval
        else:
            min_eval = math.inf
            for i in range(9):
                if tablero[i] == ' ':
                    tablero[i] = self.jugador
                    eval_actual = self.minimax(tablero, profundidad + 1, True)
                    tablero[i] = ' '
                    min_eval = min(min_eval, eval_actual)
            return min_eval

    def alfa_beta(self, tablero, profundidad, alpha, beta, es_maximizador):
        self.nodos_evaluados += 1
        puntaje = self.evaluar_tablero()
        
        if puntaje == 10: return puntaje - profundidad
        if puntaje == -10: return puntaje + profundidad
        if ' ' not in tablero: return 0
        
        if es_maximizador:
            max_eval = -math.inf
            for i in range(9):
                if tablero[i] == ' ':
                    tablero[i] = self.ia
                    eval_actual = self.alfa_beta(tablero, profundidad + 1, alpha, beta, False)
                    tablero[i] = ' '
                    max_eval = max(max_eval, eval_actual)
                    alpha = max(alpha, eval_actual)
                    if beta <= alpha: break # PODA
            return max_eval
        else:
            min_eval = math.inf
            for i in range(9):
                if tablero[i] == ' ':
                    tablero[i] = self.jugador
                    eval_actual = self.alfa_beta(tablero, profundidad + 1, alpha, beta, True)
                    tablero[i] = ' '
                    min_eval = min(min_eval, eval_actual)
                    beta = min(beta, eval_actual)
                    if beta <= alpha: break # PODA
            return min_eval

    def evaluar_tablero(self):
        lineas = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in lineas:
            if self.tablero[a] == self.tablero[b] == self.tablero[c] != ' ':
                if self.tablero[a] == self.ia:
                    return 10
                elif self.tablero[a] == self.jugador:
                    return -10
        return 0

    def verificar_estado_juego(self):
        ganador_puntaje = self.evaluar_tablero()
        
        if ganador_puntaje == 10:
            self.juego_activo = False
            self.escribir_log("\nFIN: ¡La IA ha ganado!")
            messagebox.showinfo("Fin del juego", "La IA ha ganado. ¡Es invencible!")
            return True
        elif ganador_puntaje == -10:
            # El mensaje solicitado que jamás debería mostrarse
            self.juego_activo = False
            self.escribir_log("\nFIN: ¡El Jugador ha ganado! (Error en la Matrix)")
            messagebox.showinfo("Fin del juego", "¡Felicidades, ganaste! (Aunque teóricamente esto es imposible si el algoritmo está bien)")
            return True
        elif ' ' not in self.tablero:
            self.juego_activo = False
            self.escribir_log("\nFIN: Empate.")
            messagebox.showinfo("Fin del juego", "¡Empate! Un juego perfecto por ambos lados.")
            return True
            
        return False

    def reiniciar(self):
        self.tablero = [' ' for _ in range(9)]
        self.juego_activo = True
        self.limpiar_log()
        self.escribir_log("--- PARTIDA REINICIADA ---")
        self.dibujar_tablero_lineas()

if __name__ == "__main__":
    raiz = tk.Tk()
    app = GatoApp(raiz)
    raiz.mainloop()