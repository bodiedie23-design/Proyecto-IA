import tkinter as tk
import subprocess
import sys
from tkinter import messagebox
import os

class MenuPrincipal:
    def __init__(self, master):
        self.master = master
        self.master.title("Proyecto Final - Inteligencia Artificial")
        self.master.geometry("450x550")
        self.master.config(bg="#f0f0f0")
        
        # Título principal
        tk.Label(self.master, text="Algoritmos de Búsqueda", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333333").pack(pady=(20, 5))
        tk.Label(self.master, text="Selecciona el entorno a evaluar:", font=("Arial", 12), bg="#f0f0f0", fg="#666666").pack(pady=(0, 20))
        
        # Contenedor de botones
        self.frame_botones = tk.Frame(self.master, bg="#f0f0f0")
        self.frame_botones.pack(pady=10)
        
        # Botones de los 4 problemas
        self.crear_boton("1. Búsqueda No Informada", "Frozen Lake (BFS / DFS)", "frozenlake.py", "#4a90e2")
        self.crear_boton("2. Búsqueda Informada", "Sokoban (A* / GBFS con Zobrist)", "Sokoban.py", "#d0021b")
        self.crear_boton("3. Búsqueda Local", "8 Reinas (Hill Climbing / SA)", "8 reinas.py", "#50e3c2")
        self.crear_boton("4. Búsqueda Adversaria", "Gato Invencible (Minimax / Alfa-Beta)", "Gato.py", "#f5a623")
        
        
        # Pie de página
        tk.Label(self.master, text="Desarrollado para la materia de IA", font=("Arial", 10, "italic"), bg="#f0f0f0", fg="#999999").pack(side=tk.BOTTOM, pady=20)

    def crear_boton(self, categoria, descripcion, archivo, color_borde):
        marco = tk.Frame(self.frame_botones, bg=color_borde, padx=2, pady=2)
        marco.pack(pady=10)
        
        btn = tk.Button(marco, text=f"{categoria}\n{descripcion}", font=("Arial", 12, "bold"), 
                        width=35, height=2, bg="white", relief="flat",
                        command=lambda: self.abrir_modulo(archivo))
        btn.pack()

    def abrir_modulo(self, archivo):
        # Verificar si el archivo existe en el directorio actual antes de ejecutarlo
        if not os.path.exists(archivo):
            messagebox.showerror("Error de Archivo", f"No se encontró el archivo '{archivo}'.\nAsegúrate de que esté en la misma carpeta que main.py")
            return
            
        # Lanzar el proceso independiente
        subprocess.Popen([sys.executable, archivo])

if __name__ == "__main__":
    raiz = tk.Tk()
    app = MenuPrincipal(raiz)
    raiz.mainloop()