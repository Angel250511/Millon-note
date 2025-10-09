import tkinter as tk
from tkinter import font, simpledialog, messagebox
import json
import os
import io
import re
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# --- Constante para el nombre del archivo de guardado ---
DATA_FILE = "nexus_notes_data.json"

# ---- 1. LÓGICA DE PERSISTENCIA (GUARDADO Y CARGA) ----

def load_data():
    if not os.path.exists(DATA_FILE):
        return { 
            "Realista": [
                {"titulo": "Nota Corta", "contenido": "Este texto es corto.", "anclado": False, "pos_x": 100, "pos_y": 100},
                {"titulo": "Nota Larga (con Scroll)", "contenido": "Este es un ejemplo de una nota muy, muy larga que ya no hará que el post-it crezca.\n\nEn su lugar, como el tamaño ahora es fijo y simula un post-it real de 3x3 pulgadas, aparecerá una barra de scroll a la derecha para que puedas desplazarte y leer todo el contenido sin que la nota ocupe toda la pantalla.\n\nEsta es una solución mucho más elegante y profesional para manejar grandes cantidades de texto en un espacio pequeño y definido. \n\n¡Prueba a desplazar la barra!", "anclado": False, "pos_x": 450, "pos_y": 100}
            ], 
        }
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        messagebox.showerror("Error de Carga", "No se pudo cargar el archivo de datos.")
        return {}

def write_data_to_disk():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(datos, file, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error al Guardar", f"No se pudieron guardar los datos.\nError: {e}")

def on_close():
    write_data_to_disk()
    root.destroy()

# ---- 2. LÓGICA DE LA APLICACIÓN ----

def update_notes_list(event=None):
    global current_selected_theme
    selected_indices = listbox_temas.curselection()
    if not selected_indices:
        current_selected_theme = None
        listbox_apuntes.delete(0, tk.END)
        return
    current_selected_theme = listbox_temas.get(selected_indices[0])
    listbox_apuntes.delete(0, tk.END)
    notes_for_theme = datos.get(current_selected_theme, [])
    for note in notes_for_theme:
        listbox_apuntes.insert(tk.END, note["titulo"])

def open_note_editor(event=None):
    selected_note_indices = listbox_apuntes.curselection()
    if not selected_note_indices or not current_selected_theme: return

    note_index = selected_note_indices[0]
    theme_name = current_selected_theme
    note_data = datos[theme_name][note_index]
    note_title = note_data["titulo"]
    note_content = note_data.get("contenido", "")

    editor_window = tk.Toplevel(root)
    editor_window.title(f"Editando: {note_title}")
    editor_window.geometry("600x500")

    editor_texto = tk.Text(editor_window, font=font_editor, wrap='word', bd=0, highlightthickness=1)
    editor_texto.pack(fill='both', expand=True, padx=10, pady=5)
    editor_texto.insert("1.0", note_content)

    def save_and_close_editor():
        new_content = editor_texto.get("1.0", tk.END).strip()
        datos[theme_name][note_index]["contenido"] = new_content
        write_data_to_disk()
        editor_window.destroy()
        satellite_id = f"{theme_name}_{note_index}"
        if satellite_id in open_satellites:
            open_satellites[satellite_id].destroy()
            open_satellites.pop(satellite_id, None)
            create_satellite_window(theme_name, note_index)

    editor_window.protocol("WM_DELETE_WINDOW", save_and_close_editor)
    tk.Button(editor_window, text="Guardar y Cerrar", command=save_and_close_editor).pack(pady=5)

def add_new_note():
    if not current_selected_theme: messagebox.showwarning("Atención", "Selecciona un tema."); return
    note_title = simpledialog.askstring("Nuevo Apunte", "Título:")
    if note_title and note_title.strip():
        new_note = {"titulo": note_title.strip(), "contenido": "", "anclado": False, "pos_x": 100, "pos_y": 100}
        datos[current_selected_theme].append(new_note); write_data_to_disk(); update_notes_list()

def add_new_theme():
    name = simpledialog.askstring("Nuevo Tema", "Nombre:")
    if name and name.strip():
        clean_name = name.strip()
        if clean_name in datos: messagebox.showwarning("Atención", f"El tema '{clean_name}' ya existe.")
        else: datos[clean_name] = []; listbox_temas.insert(tk.END, clean_name); write_data_to_disk()

def delete_theme():
    if not current_selected_theme: messagebox.showwarning("Atención", "Selecciona un tema."); return
    if messagebox.askyesno("Confirmar", f"¿Eliminar tema '{current_selected_theme}'?"):
        del datos[current_selected_theme]; write_data_to_disk(); populate_themes_list(); listbox_apuntes.delete(0, tk.END)

def delete_note():
    selected_note_indices = listbox_apuntes.curselection()
    if not selected_note_indices or not current_selected_theme: return
    note_index = selected_note_indices[0]; note_title = datos[current_selected_theme][note_index]["titulo"]
    if messagebox.askyesno("Confirmar", f"¿Eliminar apunte '{note_title}'?"):
        datos[current_selected_theme].pop(note_index); write_data_to_disk(); update_notes_list()

def populate_themes_list():
    listbox_temas.delete(0, tk.END)
    for tema in datos.keys(): listbox_temas.insert(tk.END, tema)

# ---- LÓGICA DE SATÉLITES ----

open_satellites = {}

def create_satellite_window(theme_name, note_index):
    note_data = datos[theme_name][note_index]
    note_content_string = note_data.get("contenido", "")
    satellite_id = f"{theme_name}_{note_index}"
    if satellite_id in open_satellites: return

    satellite = tk.Toplevel(root)
    satellite.overrideredirect(True)
    satellite.attributes("-topmost", True)
    
    try: dpi = satellite.winfo_fpixels('1i')
    except: dpi = 96 
        
    note_size_inches = 3.0
    note_size_px = int(note_size_inches * dpi)
    
    pos_x, pos_y = note_data.get("pos_x", 100), note_data.get("pos_y", 100)
    satellite.geometry(f"{note_size_px}x{note_size_px}+{pos_x}+{pos_y}")
    
    # --- LADRILLO CLAVE 1: Evita que el post-it se pueda "ajustar" ---
    satellite.resizable(False, False)
    # ----------------------------------------------------------------

    frame = tk.Frame(satellite, bg="#FFFFA5", bd=1, relief="solid")
    frame.pack(fill='both', expand=True)
    
    header_frame = tk.Frame(frame, bg="#FFFFA5")
    header_frame.pack(side="top", fill="x", padx=5, pady=5)
    
    title_label = tk.Label(header_frame, text=note_data["titulo"], font=font_normal, bg="#FFFFA5", wraplength=note_size_px - 40, justify="left")
    title_label.pack(side="left")

    content_container = tk.Frame(frame, bg="#FFFFA5")
    content_container.pack(fill="both", expand=True, padx=(10,0), pady=(0,10))

    # --- INGENIERO'S LÍNEA MODIFICADA CON ESTILOS ---
    scrollbar = tk.Scrollbar(
        content_container,
        troughcolor="#FFFFA5",          # Color del canal (fondo del post-it)
        bg="#E0DDB0",                # Color de la barra (un amarillo más oscuro)
        activebackground="#C9C799",    # Color al pasar el ratón (aún más oscuro)
        bd=0,                        # Sin borde 3D
        highlightthickness=0         # Sin borde de foco
    )
# --------------------------------------------------------
    scrollbar.pack(side="right", fill="y")

    content_text_widget = tk.Text(content_container, font=font_normal, bg="#FFFFA5", wrap="word", bd=0, 
                                  highlightthickness=0, yscrollcommand=scrollbar.set, cursor="arrow")
    content_text_widget.pack(side="left", fill="both", expand=True)
    
    scrollbar.config(command=content_text_widget.yview)
    content_text_widget.images = []

    content_text_widget.config(state="normal")
    content_text_widget.delete("1.0", tk.END)
    
    pattern = re.compile(r'(\$.*?\$)')
    parts = pattern.split(note_content_string)

    for part in parts:
        if pattern.match(part) and len(part) > 2:
            try:
                fig = plt.figure(dpi=150); fig.text(0, 0, part, fontsize=12); buf = io.BytesIO()
                fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1); plt.close(fig); buf.seek(0)
                tk_image = ImageTk.PhotoImage(Image.open(buf)); content_text_widget.images.append(tk_image)
                content_text_widget.image_create(tk.END, image=tk_image)
            except Exception: content_text_widget.insert(tk.END, f" [Fórmula Inválida] ")
        else: content_text_widget.insert(tk.END, part)
    
    content_text_widget.config(state="disabled")

    # --- LADRILLO CLAVE 2: El motor que permite mover el post-it ---
    def start_move(event): satellite.x, satellite.y = event.x, event.y
    def do_move(event):
        x, y = satellite.winfo_x() + (event.x - satellite.x), satellite.winfo_y() + (event.y - satellite.y)
        satellite.geometry(f"+{x}+{y}")
        datos[theme_name][note_index]["pos_x"], datos[theme_name][note_index]["pos_y"] = x, y
    def stop_move(event): write_data_to_disk()

    # Se vincula a todo el frame amarillo para que puedas arrastrar desde cualquier parte.
    frame.bind("<Button-1>", start_move)
    frame.bind("<B1-Motion>", do_move)
    frame.bind("<ButtonRelease-1>", stop_move)
    # -------------------------------------------------------------

    def unpin():
        datos[theme_name][note_index]["anclado"] = False; write_data_to_disk()
        open_satellites.pop(satellite_id, None); satellite.destroy()
    
    close_button = tk.Button(header_frame, text="X", command=unpin, bg="#FFFFA5", fg="#333", bd=0, font=("Segoe UI", 8, "bold"), activebackground="#E0DDB0")
    close_button.pack(side="right")
    open_satellites[satellite_id] = satellite

def toggle_pin_note():
    selected_note_indices = listbox_apuntes.curselection()
    if not selected_note_indices or not current_selected_theme: return
    note_index = selected_note_indices[0]
    note_data = datos[current_selected_theme][note_index]
    note_data["anclado"] = not note_data.get("anclado", False)
    if note_data["anclado"]:
        create_satellite_window(current_selected_theme, note_index)
    else:
        satellite_id = f"{current_selected_theme}_{note_index}"
        if satellite_id in open_satellites: open_satellites[satellite_id].destroy(); open_satellites.pop(satellite_id, None)
    write_data_to_disk()

def initialize_satellites():
    for theme, notes in datos.items():
        for i, note in enumerate(notes):
            if note.get("anclado", False): create_satellite_window(theme, i)

# ---- 3. PLANO DE LA APLICACIÓN (UI) ----

root = tk.Tk()
datos = load_data()
current_selected_theme = None
font_titulo = font.Font(family="Segoe UI", size=12, weight="bold")
font_normal = font.Font(family="Segoe UI", size=11)
font_editor = font.Font(family="Consolas", size=11)
root.title("Millon note")
root.geometry("700x600")
root.protocol("WM_DELETE_WINDOW", on_close)

sidebar=tk.Frame(root,bg="#282828",width=250);sidebar.pack_propagate(False);sidebar.pack(side='left',fill='y');btn_temas_header=tk.Button(sidebar,text="Temas",font=font_titulo,bg="#404040",fg="white",bd=0);btn_temas_header.pack(pady=20,padx=10,fill='x');listbox_temas=tk.Listbox(sidebar,font=font_normal,bg="#282828",fg="white",bd=0,highlightthickness=0,selectbackground="#007acc",exportselection=False);listbox_temas.pack(fill='both',expand=True,padx=10,pady=5);listbox_temas.bind('<<ListboxSelect>>',update_notes_list);bottom_frame=tk.Frame(sidebar,bg="#282828");bottom_frame.pack(side='bottom',fill='x',pady=10);btn_add_theme=tk.Button(bottom_frame,text="+ Tema",command=add_new_theme,font=font_normal,bg="#404040",fg="white",bd=0);btn_add_theme.pack(side='left',fill='x',expand=True,padx=(10,5));btn_delete_theme=tk.Button(bottom_frame,text="– Tema",command=delete_theme,font=font_normal,bg="#c94c4c",fg="white",bd=0);btn_delete_theme.pack(side='left',fill='x',expand=True,padx=(5,10));
notes_frame=tk.Frame(root,bg="#f0f0f0");notes_frame.pack(side='left',fill='both',expand=True);notes_header_frame=tk.Frame(notes_frame,bg="#f0f0f0");notes_header_frame.pack(fill='x',padx=10,pady=10);tk.Label(notes_header_frame,text="Apuntes",font=font_titulo,bg="#f0f0f0").pack(side='left');btn_pin_note=tk.Button(notes_header_frame,text="📌",font=font_titulo,command=toggle_pin_note);btn_pin_note.pack(side='right');btn_delete_note=tk.Button(notes_header_frame,text="–",font=font_titulo,command=delete_note,bg="#c94c4c",fg="white");btn_delete_note.pack(side='right',padx=5);btn_add_note=tk.Button(notes_header_frame,text="+",font=font_titulo,command=add_new_note);btn_add_note.pack(side='right',padx=5);listbox_apuntes=tk.Listbox(notes_frame,font=font_normal,bd=0,highlightthickness=0);listbox_apuntes.pack(fill='both',expand=True,padx=10,pady=5);listbox_apuntes.bind('<Double-1>',open_note_editor);

populate_themes_list()
if datos: listbox_temas.selection_set(0); update_notes_list(None)
initialize_satellites()

# ---- 4. INICIAR LA APLICACIÓN ----
root.mainloop()
