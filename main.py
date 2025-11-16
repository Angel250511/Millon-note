# main.py
# Punto de entrada de la aplicación Nexus Notes.
# Su única responsabilidad es inicializar y ejecutar la aplicación.
import tkinter as tk
from app_logic import Millon_note


if __name__ == "__main__":
    root = tk.Tk()
    app = Millon_note(root)
    root.mainloop()