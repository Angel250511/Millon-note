# ui_builder.py
# Módulo que se encarga exclusivamente de construir la interfaz de usuario principal.
# No contiene lógica de negocio, solo la creación y disposición de widgets.

import tkinter as tk
from tkinter import ttk, font
import sv_ttk
import platform

# Intenta importar pywinstyles si está disponible
try:
    import pywinstyles
except ImportError:
    pywinstyles = None

class UIBuilder:
    def __init__(self, app):
        """
        Constructor de la clase UIBuilder.
        
        Parameters
        ----------
        app : Millon_note
            Referencia a la aplicación principal para conectar comandos
        """

        self.app = app # Referencia a la aplicación principal para conectar comandos
        self.root = app.root
        
    def setup_fonts(self):
        """
        Configura los estilos de fuente para la aplicación.
        
        Según la plataforma en la que se esté ejecutando, se
        seleccionan los nombres de fuente y tamaños para los estilos de
        fuente de la aplicación.
        
        Se establecen las siguientes variables:
        
        - self.app.font_titulo: Fuente para los títulos.
        - self.app.font_normal: Fuente para el texto normal.
        - self.app.font_editor: Fuente para el editor de texto.
        """
        if platform.system() == "Windows":
            font_normal = "Segoe UI Variable"
            font_editor = "Cascadia Code"
        elif platform.system() == "Darwin":
            font_normal = "Helvetica Neue"
            font_editor = "Menlo"
        else:
            font_normal = "DejaVu Sans"
            font_editor = "DejaVu Sans Mono"
            
        self.app.font_titulo = font.Font(family=font_normal, size=14, weight="bold")
        self.app.font_normal = font.Font(family=font_normal, size=11)
        self.app.font_editor = font.Font(family=font_editor, size=11)

    def setup_ui(self):
        """
        Configura la interfaz de usuario principal.
        
        Establece el título de la ventana, su tamaño y su estilo.
        Configura los estilos de los widgets y los coloca en la ventana.
        Crea los frames y los widgets necesarios para la barra lateral y la sección de notas.
        """
        """
        Configura la interfaz de usuario principal.
    
        Establece el título de la ventana, su tamaño y su estilo.
        Configura los estilos de los widgets y los coloca en la ventana.
        Crea los frames y los widgets necesarios para la barra lateral y la sección de notas.
        """
        self.root.title("Nexus Notes")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.app.on_close)
        if platform.system() == "Windows" and pywinstyles:
            pywinstyles.apply_style(self.root, "acrylic")
        sv_ttk.set_theme(self.app.current_theme)

        style = ttk.Style()
        style.configure("Danger.TButton", foreground="white", background="#c94c4c")
        style.configure("Toolbutton.TButton", padding=5)
        style.configure("Action.TButton", font=self.app.font_normal, anchor="w")
        
        self.app.sidebar_toggle_frame = ttk.Frame(self.root, style="Card.TFrame")
        ttk.Button(self.app.sidebar_toggle_frame, text=self.app.ICONS["show_sidebar"], command=self.app.toggle_sidebar, width=3, style="Toolbutton.TButton").pack(pady=5, padx=5)
        
        self.app.sidebar = ttk.Frame(self.root, width=250, style="Card.TFrame")
        self.app.sidebar.pack_propagate(False)
        
        header_sidebar_frame = ttk.Frame(self.app.sidebar)
        header_sidebar_frame.pack(fill='x', padx=20, pady=(20, 10))
        ttk.Button(header_sidebar_frame, text=self.app.ICONS["hide_sidebar"], command=self.app.toggle_sidebar, width=3, style="Toolbutton.TButton").pack(side='left')
        ttk.Label(header_sidebar_frame, text="Topics", font=self.app.font_titulo).pack(side='left', padx=10)
        
        self.app.listbox_temas = tk.Listbox(self.app.sidebar, font=self.app.font_normal, bd=0, highlightthickness=0, exportselection=False)
        self.app.listbox_temas.pack(fill='both', expand=True, padx=10, pady=5)
        self.app.listbox_temas.bind('<<ListboxSelect>>', self.app.update_notes_list)
        
        bottom_frame = ttk.Frame(self.app.sidebar)
        bottom_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(bottom_frame, text=f" {self.app.ICONS['add']}   New Topic", command=self.app.add_new_theme, compound="left", style="Action.TButton").pack(fill='x', padx=10, pady=(0, 5))
        # ui_builder.py, dentro de setup_ui

# ... (línea del botón "Nuevo Tema") ...

# --- INICIO DEL CÓDIGO DE DEPURACIÓN ---
    

# Esta es la línea que falla

# ... (resto del código) ...
        ttk.Button(bottom_frame, text=f" {self.app.ICONS['rename']}   Rename", command=self.app.rename_theme, compound="left", style="Action.TButton").pack(fill='x', padx=10, pady=(0, 5))
        ttk.Button(bottom_frame, text=f" {self.app.ICONS['delete']}   Delete Topic", command=self.app.delete_theme, compound="left", style="Danger.TButton").pack(fill='x', padx=10)

        notes_frame = ttk.Frame(self.root, style="Card.TFrame")
        notes_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        notes_header_frame = ttk.Frame(notes_frame)
        notes_header_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(notes_header_frame, font=self.app.font_titulo).pack(side='left')
        
        buttons = [("theme", self.app.toggle_theme, 0), ("pin", self.app.toggle_pin_note, 5), ("delete", self.app.delete_note, 5), 
                   ("rename", self.app.rename_note, 5), ("image", self.app.add_new_image, 5), ("add", self.app.add_new_note, 5)]
        for icon, cmd, padx in buttons:
            ttk.Button(notes_header_frame, text=self.app.ICONS[icon], command=cmd, style="Toolbutton.TButton").pack(side='right', padx=(0,padx))

        search_frame = ttk.Frame(notes_frame)
        search_frame.pack(fill='x', padx=10, pady=(0, 5))
        self.app.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.app.search_var, font=self.app.font_normal, width=40)
        search_entry.pack(side='left', fill='x', expand=True, ipady=2)
        search_entry.bind('<Return>', self.app._refresh_notes_view)
        ttk.Button(search_frame, text="✖", command=self.app.clear_search, style="Toolbutton.TButton", width=3).pack(side='right', padx=(5,0))
        ttk.Button(search_frame, text="🔍", command=self.app._refresh_notes_view, style="Toolbutton.TButton", width=3).pack(side='right')

        self.app.listbox_apuntes = tk.Listbox(notes_frame, font=self.app.font_normal, bd=0, highlightthickness=0, exportselection=False)
        self.app.listbox_apuntes.pack(fill='both', expand=True, padx=10, pady=5)
        self.app.listbox_apuntes.bind('<Double-1>', self.app.open_note_editor)