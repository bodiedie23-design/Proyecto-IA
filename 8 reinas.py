import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import random
import math

class ReinasApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Búsqueda Local - 8 Reinas")
        
        self.n = 8
        self.tamano_celda = 50
        self.animando = False
        
        # Estado: lista de 8 enteros (índice = columna, valor = fila de la reina)
        self.estado_actual = self.generar_estado_aleatorio()
        
        # Contenedor Principal (Izquierda: Tablero | Derecha: Logs)
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Panel de Logs
        tk.Label(self.right_frame, text="Iteraciones del Algoritmo", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.right_frame, width=45, height=25, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Etiqueta de Niveles (Omitida / N/A como solicitaste)
        self.frame_niveles = tk.Frame(self.left_frame)
        self.frame_niveles.pack(pady=5)
        tk.Label(self.frame_niveles, text="Niveles: N/A (Problema de estado único)", font=("Arial", 10, "italic"), fg="gray").pack()
        
        # Canvas para el tablero de ajedrez
        self.canvas = tk.Canvas(self.left_frame, width=self.n * self.tamano_celda, height=self.n * self.tamano_celda, bg="white", borderwidth=1, relief="solid")
        self.canvas.pack(pady=10)
        
        # Controles
        self.frame_botones = tk.Frame(self.left_frame)
        self.frame_botones.pack(pady=5)
        
        self.btn_hc = tk.Button(self.frame_botones, text="Hill Climbing", command=self.ejecutar_hill_climbing, bg="lightblue", font=("Arial", 11, "bold"))
        self.btn_hc.pack(side=tk.LEFT, padx=5)
        
        self.btn_rs = tk.Button(self.frame_botones, text="Recocido Simulado", command=self.ejecutar_recocido, bg="lightgreen", font=("Arial", 11, "bold"))
        self.btn_rs.pack(side=tk.LEFT, padx=5)
        
        self.btn_mezclar = tk.Button(self.frame_botones, text="Mezclar Reinas", command=self.mezclar_tablero, bg="#d9534f", fg="white", font=("Arial", 11, "bold"))
        self.btn_mezclar.pack(side=tk.LEFT, padx=5)
        
        self.escribir_log("--- SISTEMA LISTO ---")
        self.escribir_log("Tablero inicializado aleatoriamente.")
        self.dibujar_tablero(self.estado_actual)

    def escribir_log(self, texto):
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)

    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)

    def generar_estado_aleatorio(self):
        return [random.randint(0, self.n - 1) for _ in range(self.n)]

    def mezclar_tablero(self):
        if self.animando: return
        self.estado_actual = self.generar_estado_aleatorio()
        self.limpiar_log()
        self.escribir_log("--- TABLERO MEZCLADO ---")
        self.escribir_log(f"Ataques actuales: {self.calcular_ataques(self.estado_actual)}")
        self.dibujar_tablero(self.estado_actual)

    def calcular_ataques(self, estado):
        # Función de costo (Heurística): Cuenta cuántos pares de reinas se atacan
        ataques = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                # Misma fila o misma diagonal
                if estado[i] == estado[j] or abs(estado[i] - estado[j]) == abs(i - j):
                    ataques += 1
        return ataques

    def generar_vecinos(self, estado):
        vecinos = []
        for col in range(self.n):
            for fila in range(self.n):
                if estado[col] != fila:
                    nuevo_estado = list(estado)
                    nuevo_estado[col] = fila
                    vecinos.append(nuevo_estado)
        return vecinos

    def dibujar_tablero(self, estado, resaltados=None):
        self.canvas.delete("all")
        for r in range(self.n):
            for c in range(self.n):
                x1, y1 = c * self.tamano_celda, r * self.tamano_celda
                x2, y2 = x1 + self.tamano_celda, y1 + self.tamano_celda
                
                # Patrón de ajedrez
                color = "#ffce9e" if (r + c) % 2 == 0 else "#d18b47"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Dibujar Reina
                if estado[c] == r:
                    self.canvas.create_text(x1 + self.tamano_celda/2, y1 + self.tamano_celda/2, 
                                            text="♛", font=("Arial", 28), fill="black")

    def toggle_botones(self, estado):
        estado_tk = tk.DISABLED if estado == False else tk.NORMAL
        self.btn_hc.config(state=estado_tk)
        self.btn_rs.config(state=estado_tk)
        self.btn_mezclar.config(state=estado_tk)

    def ejecutar_hill_climbing(self):
        self.limpiar_log()
        self.escribir_log("--- INICIANDO BÚSQUEDA: HILL CLIMBING ---")
        self.animando = True
        self.toggle_botones(False)
        
        actual = list(self.estado_actual)
        ataques_actuales = self.calcular_ataques(actual)
        
        def iteracion_hc():
            nonlocal actual, ataques_actuales
            
            if ataques_actuales == 0:
                self.escribir_log("\n¡SOLUCIÓN PERFECTA ENCONTRADA! (0 ataques)")
                self.animando = False
                self.toggle_botones(True)
                messagebox.showinfo("Éxito", "¡Problema resuelto con Hill Climbing!")
                return
                
            vecinos = self.generar_vecinos(actual)
            mejor_vecino = None
            menor_ataque = ataques_actuales
            
            # Buscar el mejor vecino
            for vecino in vecinos:
                ataque_vecino = self.calcular_ataques(vecino)
                if ataque_vecino < menor_ataque:
                    menor_ataque = ataque_vecino
                    mejor_vecino = vecino
                    
            if mejor_vecino is None:
                self.escribir_log(f"\n[!] ATASCADO EN ÓPTIMO LOCAL. Ataques: {ataques_actuales}")
                self.escribir_log("El algoritmo no puede encontrar un estado mejor. Mezcla y reintenta.")
                self.animando = False
                self.toggle_botones(True)
                messagebox.showwarning("Atascado", "Óptimo local alcanzado. ¡Mezcla y reintenta!")
                return
                
            self.escribir_log(f"Mejora encontrada. Ataques reducidos: {ataques_actuales} -> {menor_ataque}")
            actual = mejor_vecino
            ataques_actuales = menor_ataque
            self.estado_actual = actual
            self.dibujar_tablero(actual)
            
            self.master.after(200, iteracion_hc) # Pausa de 200ms para animar

        self.escribir_log(f"Ataques iniciales: {ataques_actuales}")
        iteracion_hc()

    def ejecutar_recocido(self):
        self.limpiar_log()
        self.escribir_log("--- INICIANDO: RECOCIDO SIMULADO (SA) ---")
        self.animando = True
        self.toggle_botones(False)
        
        actual = list(self.estado_actual)
        ataques_actuales = self.calcular_ataques(actual)
        temperatura = 100.0
        tasa_enfriamiento = 0.95
        iteracion = 1
        
        def iteracion_rs():
            nonlocal actual, ataques_actuales, temperatura, iteracion
            
            if ataques_actuales == 0:
                self.escribir_log("\n¡SOLUCIÓN PERFECTA ENCONTRADA! (0 ataques)")
                self.animando = False
                self.toggle_botones(True)
                messagebox.showinfo("Éxito", "¡Problema resuelto con Recocido Simulado!")
                return
                
            if temperatura <= 0.1:
                self.escribir_log(f"\n[!] SISTEMA ENFRIADO. Ataques finales: {ataques_actuales}")
                self.animando = False
                self.toggle_botones(True)
                messagebox.showwarning("Fin", "Temperatura mínima alcanzada sin solución perfecta. ¡Intenta de nuevo!")
                return

            vecinos = self.generar_vecinos(actual)
            siguiente = random.choice(vecinos)
            ataques_siguiente = self.calcular_ataques(siguiente)
            
            delta_e = ataques_actuales - ataques_siguiente
            
            # Condición de aceptación de Boltzmann
            if delta_e > 0 or random.random() < math.exp(delta_e / temperatura):
                if delta_e < 0:
                    self.escribir_log(f"Iter {iteracion} | T={temperatura:.1f} | Acepta estado PEOR (Delta: {delta_e})")
                else:
                    self.escribir_log(f"Iter {iteracion} | T={temperatura:.1f} | Mejora: {ataques_actuales}->{ataques_siguiente}")
                
                actual = siguiente
                ataques_actuales = ataques_siguiente
                self.estado_actual = actual
                self.dibujar_tablero(actual)
            
            temperatura *= tasa_enfriamiento
            iteracion += 1
            
            self.master.after(50, iteracion_rs) # Más rápido porque SA requiere más iteraciones

        self.escribir_log(f"Ataques iniciales: {ataques_actuales} | T_Inicial: {temperatura}")
        iteracion_rs()

if __name__ == "__main__":
    raiz = tk.Tk()
    app = ReinasApp(raiz)
    raiz.mainloop()