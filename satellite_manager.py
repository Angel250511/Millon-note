# satellite_manager.py
# Módulo dedicado a la creación y gestión de las ventanas "satélite" (notas flotantes).
# Encapsula toda la lógica de renderizado, movimiento y redimensionamiento.
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
import io
import re
from ui_components import CustomScrollbar # Importamos nuestro componente

class SatelliteManager:

    def __init__(self, app):
        """
        Constructor de la clase SatelliteManager.

        Parameters
        ----------
        app : Millon_note
            Referencia a la aplicación principal para conectar comandos
        """
        
        self.app = app
        self.root = app.root
        
    def create_rounded_rectangle_image(self, w, h, r, c):
        """
        Crea una imagen redonda con un rectángulo con esquina redondeada.

        Parameters
        ----------
        w : int
            Ancho de la imagen
        h : int
            Alto de la imagen
        r : int
            Radio de la esquina
        c : str
            Color del rectángulo

        Returns
        -------
        ImageTk.PhotoImage
            Imagen redonda con el rectángulo
        """
        img = Image.new("RGBA", (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0,0,w,h), r, fill=c)
        return ImageTk.PhotoImage(img)

    def create_satellite_window(self, theme_name, note_index):
        """
        Crea una ventana flotante asociada a una nota.

        Parameters
        ----------
        theme_name : str
            Nombre del tema al que pertenece la nota.
        note_index : int
            Índice de la nota en el tema.

        Returns
        -------
        None
        """
        note_data = self.app.datos[theme_name][note_index]
        note_id = note_data['id']
        sat_id = f"{theme_name}_{note_id}"
        if sat_id in self.app.open_satellites: return
        
        CHROMA = '#abcdef'
        satellite = tk.Toplevel(self.root)
        satellite.overrideredirect(True)
        satellite.config(bg=CHROMA)
        satellite.attributes('-transparentcolor', CHROMA, "-topmost", True)
        
        pos_x = note_data.get("pos_x", 100)
        pos_y = note_data.get("pos_y", 100)
        
        def start_move(e): satellite.x, satellite.y = e.x, e.y
        def do_move(e):
            """
            Mueve la ventana flotante a una nueva posición

            Parameters
            ----------
            e : Event
                Evento de movimiento del ratón

            Returns
            -------
            None
            """
            x = satellite.winfo_x() + (e.x - satellite.x)
            y = satellite.winfo_y() + (e.y - satellite.y)
            satellite.geometry(f"+{x}+{y}")
            note_data.update({'pos_x': x, 'pos_y': y})

        if note_data.get("type") == "image":
            try:
                img_orig = Image.open(note_data["path"])
                satellite.original_image = img_orig
                w, h = img_orig.size
                satellite.aspect = h/w if w > 0 else 1
                
                nw = note_data.get("width", min(w, 500))
                nh = int(nw * satellite.aspect)

                tk_img = ImageTk.PhotoImage(img_orig.resize((nw,nh), Image.Resampling.LANCZOS))
                img_label = tk.Label(satellite, image=tk_img, bg=CHROMA, bd=0)
                img_label.image = tk_img
                img_label.pack()
                
                satellite.geometry(f"{nw}x{nh}+{pos_x}+{pos_y}")
                
                menu = tk.Menu(satellite, tearoff=0)
                menu.add_command(label="Desanclar", command=lambda: self.app.toggle_pin_note(theme=theme_name, manual_idx=note_index))
                img_label.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
                
                def save_geometry(e):
                    """
                    Guarda la geometría actual de la ventana flotante en la base de datos.

                    Parameters
                    ----------
                    e : Event
                        Evento de soltar el botón izquierdo del ratón

                    Returns
                    -------
                    None
                    """
                    note_data.update({
                        'pos_x': satellite.winfo_x(), 'pos_y': satellite.winfo_y(), 
                        'width': satellite.winfo_width()
                    })
                    self.app.data_manager.update_note(note_data['id'], note_data)

                img_label.bind("<Button-1>", start_move)
                img_label.bind("<B1-Motion>", do_move)
                img_label.bind("<ButtonRelease-1>", save_geometry)

                handle = tk.Frame(satellite, bg='gray', width=10, height=10, cursor="bottom_right_corner")
                handle.place(relx=1, rely=1, anchor='se')
                
                def start_resize(e):
                    """
                    Comienza la geometría actual de la ventana flotante y guarda los valores
                    de ancho y alto en los atributos de la ventana flotante.

                    Parameters
                    ----------
                    e : Event
                        Evento de presionar el botón izquierdo del ratón

                    Returns
                    -------
                        None
                        """
                    satellite.sw, satellite.sh = satellite.winfo_width(), satellite.winfo_height()
                    satellite.sx, satellite.sy = e.x_root, e.y_root
                
                def do_resize(e):
                    """
                    Redimensiona la ventana flotante en tiempo real.

                    Parameters
                    ----------
                    e : Event
                        Evento de movimiento del ratón

                    Returns
                    -------
                    None
                    """
                    nw = max(50, satellite.sw + (e.x_root - satellite.sx))
                    nh = int(nw * satellite.aspect)
                    new_tk_img = ImageTk.PhotoImage(satellite.original_image.resize((nw,nh), Image.Resampling.LANCZOS))
                    img_label.config(image=new_tk_img)
                    img_label.image = new_tk_img
                    satellite.geometry(f"{nw}x{nh}")
                
                handle.bind("<Button-1>", start_resize)
                handle.bind("<B1-Motion>", do_resize)
                handle.bind("<ButtonRelease-1>", save_geometry)
            
            except FileNotFoundError:
                satellite.destroy()
                messagebox.showerror("Error de Imagen", f"No se pudo encontrar el archivo de imagen para '{note_data['titulo']}'.\n\nPuede que haya sido eliminado.")
            except Exception as e:
                satellite.destroy()
                messagebox.showerror("Error", f"No se pudo cargar la imagen flotante:\n{e}")
        else:
            bg = note_data.get("color", self.app.POSTIT_COLORS["Amarillo Clásico"])
            fg = "#000000"
            try: px_size = int(3.0 * satellite.winfo_fpixels('1i'))
            except: px_size = 288
            
            satellite.geometry(f"{px_size}x{px_size}+{pos_x}+{pos_y}")
            satellite.resizable(False, False)
            
            bg_label = tk.Label(satellite, bd=0, bg=CHROMA)
            bg_img = self.create_rounded_rectangle_image(px_size, px_size, 15, bg)
            bg_label.config(image=bg_img)
            bg_label.image = bg_img
            bg_label.pack(fill="both", expand=True)
            
            header = tk.Frame(bg_label, bg=bg)
            header.pack(side="top", fill="x", padx=(15, 5), pady=(10, 5))
            
            # No mostramos el título en las ventanas satélite.
            # Dejamos el header vacío (el botón de cerrar se añadirá más abajo).
            # Si en el futuro quieres reactivar el título, podemos añadir una opción de configuración.
            
            # --- INICIO DE LA LÓGICA DE CENTRADO DEFINITIVA ---
            temp_container = tk.Frame(bg_label)
            temp_text = tk.Text(temp_container, font=self.app.font_normal, wrap="word", bd=0, highlightthickness=0)
            temp_scrollbar = CustomScrollbar(temp_container, command=temp_text.yview)
            temp_text.config(yscrollcommand=temp_scrollbar.set)
            
            temp_text.images = []
            for part in re.compile(r'(\$.*?\$)').split(note_data.get("contenido", "")):
                if re.match(r'(\$.*?\$)', part) and len(part) > 2:
                    try:
                        fig = plt.figure(dpi=150); fig.text(0,0,part,fontsize=12,color=fg)
                        buf = io.BytesIO(); fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1); plt.close(fig); buf.seek(0)
                        tk_img = ImageTk.PhotoImage(Image.open(buf)); temp_text.images.append(tk_img)
                        temp_text.image_create(tk.END, image=tk_img)
                    except: temp_text.insert(tk.END, " [Fórmula Inválida] ")
                else: temp_text.insert(tk.END, part)
            
            satellite.update_idletasks()
            lo, hi = temp_scrollbar.get()
            temp_container.destroy()

            if lo == 0.0 and hi == 1.0:
                content_wrapper = tk.Frame(bg_label, bg=bg)
                content_wrapper.pack(expand=True, fill="both", padx=15, pady=(0, 15))
                plain_content = re.sub(r'\$.*?\$', '[Fórmula]', note_data.get("contenido", ""))
                content_label = tk.Label(content_wrapper, text=plain_content, font=self.app.font_normal, bg=bg, fg=fg, justify="center")
                content_label.place(relx=0.5, rely=0.5, anchor="center")
                for w in [content_wrapper, content_label]:
                    w.bind("<Button-1>", start_move)
                    w.bind("<B1-Motion>", do_move)
                    w.bind("<ButtonRelease-1>", lambda e, n=note_data: self.app.data_manager.update_note(n['id'], n))
            else:
                container = tk.Frame(bg_label, bg=bg)
                container.pack(fill="both", expand=True, padx=(15,0), pady=(0,15))
                try:
                    r, g, b = self.root.winfo_rgb(bg); r, g, b = r//256, g//256, b//256
                    thumb_c = f'#{max(0,r-35):02x}{max(0,g-35):02x}{max(0,b-35):02x}'
                    hover_c = f'#{max(0,r-55):02x}{max(0,g-55):02x}{max(0,b-55):02x}'
                except: thumb_c, hover_c = "#C0C0C0", "#A0A0A0"
                
                text_widget = tk.Text(container, font=self.app.font_normal, bg=bg, fg=fg, wrap="word", bd=0, highlightthickness=0, cursor="arrow")
                scrollbar = CustomScrollbar(container, command=text_widget.yview, troughcolor=bg, thumbcolor=thumb_c, hovercolor=hover_c)
                text_widget.config(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                text_widget.pack(side="left", fill="both", expand=True)
                satellite.text_widget = text_widget
                
                def on_mouse_wheel(event):
                    if event.num == 5 or event.delta < 0: text_widget.yview_scroll(1, "units")
                    elif event.num == 4 or event.delta > 0: text_widget.yview_scroll(-1, "units")
                for widget in [text_widget, scrollbar]:
                    widget.bind("<MouseWheel>", on_mouse_wheel); widget.bind("<Button-4>", on_mouse_wheel); widget.bind("<Button-5>", on_mouse_wheel)
                
                text_widget.images = []; text_widget.config(state="normal"); text_widget.delete("1.0", tk.END)
                for part in re.compile(r'(\$.*?\$)').split(note_data.get("contenido", "")):
                    if re.match(r'(\$.*?\$)', part) and len(part) > 2:
                        try:
                            fig = plt.figure(dpi=150); fig.text(0,0,part,fontsize=12,color=fg)
                            buf = io.BytesIO(); fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1); plt.close(fig); buf.seek(0)
                            tk_img = ImageTk.PhotoImage(Image.open(buf)); text_widget.images.append(tk_img)
                            text_widget.image_create(tk.END, image=tk_img)
                        except Exception as e: print(f"Error: {e}"); text_widget.insert(tk.END, " [Fórmula Inválida] ")
                    else: text_widget.insert(tk.END, part)
                text_widget.config(state="disabled")
            # --- FIN DE LA LÓGICA DE CENTRADO ---

            for w in [bg_label, header]:
                w.bind("<Button-1>", start_move)
                w.bind("<B1-Motion>", do_move)
                w.bind("<ButtonRelease-1>", lambda e, n=note_data: self.app.data_manager.update_note(n['id'], n))

            # Reemplaza la línea original por esta. Pasamos el ID de la nota, que es la verdad absoluta.
            note_id = note_data['id']
            close_btn = tk.Button(header, text="✖", command=lambda: self.app.toggle_pin_note(note_id=note_id, theme=theme_name), bg=bg, fg=fg, bd=0, font=("Segoe UI", 8, "bold"))

            close_btn.pack(side="right")
        
        self.app.open_satellites[sat_id] = satellite

    def initialize_satellites(self):
        """
        Inicializa las ventanas satélite correspondientes a las notas ancladas.
        """
        
        for theme, notes in list(self.app.datos.items()):
            for i, note in enumerate(notes):
                if note.get("anclado", False):
                    self.create_satellite_window(theme, i)