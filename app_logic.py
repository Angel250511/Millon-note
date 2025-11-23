# app_logic.py (Versión Final del Ingeniero - Robusta y Clara)
# El "cerebro" de la aplicación. Orquesta los otros módulos.
# Contiene la lógica de negocio y el estado de la aplicación.
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
import time
import platform
import sv_ttk
from config import DATA_FILE, IMAGE_DIR, ICONS, POSTIT_COLORS
from ui_components import CustomInputDialog, ColorPickerDialog
from data_manager import DataManager
from satellite_manager import SatelliteManager
from ui_builder import UIBuilder


try:
    import pywinstyles
except ImportError:
    pywinstyles = None

class Millon_note:
    """
    Clase principal que encapsula toda la lógica y el estado de la aplicación.
    Actúa como el controlador central, coordinando la UI, los datos y las acciones del usuario.
    """
    def __init__(self, root):
        # --- 1. Inicialización y Configuración del Sistema ---
        """
        Constructor de la clase Millon_note.

        Inicializa la aplicación Nexus Notes con la ventana principal dada.
        Carga los datos de la base de datos y configura el estado de la aplicación.
        Inicializa la UI y el gestor de satélites flotantes.
        """
        self.root = root
       # Definimos la rutas y archivos de la aplicación.
        self.IMAGE_DIR = IMAGE_DIR
        self.ICONS = ICONS
        self.POSTIT_COLORS = POSTIT_COLORS
        #creamos la carpeta de imagenes si no existe
        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)
        # Inicializamos la base de datos
        self.data_manager = DataManager(DATA_FILE)

        # Cargamos los datos de la base de datos
        self.datos, self.app_settings = self.data_manager.load_data()
        self.current_theme = self.app_settings.get("theme", "dark")
        self.sidebar_visible = self.app_settings.get("sidebar_visible", True)
        # Inicializamos el estado de la aplicación
        self.current_selected_theme = None
        self.open_satellites = {}
        self.listbox_to_note_id_map = {}
        # Inicializamos la UI
        self.ui_builder = UIBuilder(self)
        self.satellite_manager = SatelliteManager(self)

        # --- 2. Arranque del Sistema ---
        # Configuramos los fondos y los estilos
        self.ui_builder.setup_fonts()
        self.ui_builder.setup_ui()

        self._initialize_view()
        self.satellite_manager.initialize_satellites()

    def _initialize_view(self):
        """Configura el estado inicial de la vista principal."""
        self.populate_themes_list()
        self.style_listboxes()
        if self.sidebar_visible:
            self.sidebar.pack(side='left', fill='y', padx=(5,0), pady=5)
        else:
            self.sidebar_toggle_frame.pack(side='left', fill='y', padx=(5,0), pady=5)

        if self.datos:
            self.listbox_temas.selection_set(0)
            self.listbox_temas.event_generate("<<ListboxSelect>>")

    def on_close(self):
        self.data_manager.close()
        self.root.destroy()

    # --- Métodos de Ayuda Internos (Lógica a prueba de fallos) ---

    def _get_selected_note_id(self):
        """Obtiene el ID de la nota seleccionada en la Listbox de forma segura."""
        if not self.listbox_apuntes.curselection():
            return None
        listbox_index = self.listbox_apuntes.curselection()[0]
        return self.listbox_to_note_id_map.get(listbox_index)

    def _get_note_by_id(self, note_id):
        """Busca una nota en la estructura de datos en memoria por su ID único."""
        if not self.current_selected_theme or not note_id:
            return None
        for note in self.datos.get(self.current_selected_theme, []):
            if note['id'] == note_id:
                return note
        return None

    def _refresh_notes_view(self, select_last=False):
        """Refresca la lista de apuntes en la UI, manteniendo la consistencia del mapeo ID."""
        self.listbox_apuntes.delete(0, tk.END)
        self.listbox_to_note_id_map.clear()
        search_term = self.search_var.get().lower()

        if not self.current_selected_theme or self.current_selected_theme not in self.datos:
            return

        listbox_index = 0
        for note in self.datos[self.current_selected_theme]:
            titulo = note.get("titulo", "").lower()
            contenido = str(note.get("contenido", "")).lower()

            if search_term in titulo or search_term in contenido:
                prefix = f"{self.ICONS['image']} " if note.get("type") == "image" else ""
                self.listbox_apuntes.insert(tk.END, prefix + note.get("titulo", "Sin Título"))
                self.listbox_to_note_id_map[listbox_index] = note['id']
                listbox_index += 1

        if select_last and self.listbox_apuntes.size() > 0:
            self.listbox_apuntes.selection_set(tk.END)

    # --- Lógica de la Aplicación (Acciones del Usuario) ---

    def update_notes_list(self, event=None):
        """
        Actualiza la lista de apuntes en la UI cuando se selecciona un nuevo tema.
        """

        if not self.listbox_temas.curselection():
            self.current_selected_theme = None
            self._refresh_notes_view()
            return
        self.current_selected_theme = self.listbox_temas.get(self.listbox_temas.curselection()[0])
        self.search_var.set("")
        self._refresh_notes_view()

    def add_new_note(self):
        """
        Agrega una nota de texto en la UI actual.

        Llama a su propio método para agregar un item a la lista de apuntes.
        """

        self._add_new_item(is_image=False)

    def add_new_image(self):
        """
        Agrega una nota de imagen en la UI actual.

        Llama a su propio método para agregar un item a la lista de apuntes.
        """
        self._add_new_item(is_image=True)

    def _add_new_item(self, is_image=False):
        """
        Agrega una nota de texto o imagen en la UI actual.

        Parámetros:
            is_image (bool): Verdadero si la nota es una imagen o no.

        Devuelve:
            None

        Notas:
            - Si no hay un tema seleccionado, se muestra un aviso y no se hace nada.
            - Si el usuario cancela la selección de la nota, no se hace nada.
            - Si el usuario selecciona una imagen, se la guarda en la carpeta correspondiente y se
              agrega a la lista de apuntes.
            - Si el usuario selecciona un apunte de texto, se agrega a la lista de apuntes con el título
              y contenido correspondientes.
        """
        if not self.current_selected_theme:
            messagebox.showwarning("Atención", "Selecciona un tema primero.")
            return

        if is_image:
            filepath = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
            if not filepath: return
            prompt_title, initial_value = "Título para la imagen:", os.path.basename(filepath)
        else:
            prompt_title, initial_value = "Título del apunte:", ""

        note_title_str = CustomInputDialog(self.root, "Nuevo Apunte", prompt_title, initial_value, self.font_normal).show()
        if not note_title_str or not note_title_str.strip():
            return

        note_title = note_title_str.strip()
        new_note_dict = {"titulo": note_title, "anclado": False}

        if is_image:
            try:
                _, ext = os.path.splitext(filepath)
                dest_path = os.path.join(self.IMAGE_DIR, f"{int(time.time() * 1000)}{ext}")
                shutil.copy(filepath, dest_path)
                new_note_dict.update({"type": "image", "path": dest_path, "pos_x": 120, "pos_y": 120})
            except (IOError, OSError) as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")
                return
        else:
            color = ColorPickerDialog(self.root, self.POSTIT_COLORS, self.font_normal).show()
            if not color: return
            new_note_dict.update({"type": "text", "contenido": "", "pos_x": 100, "pos_y": 100, "color": color})

        new_id = self.data_manager.add_note(self.current_selected_theme, new_note_dict)
        if new_id:
            new_note_dict['id'] = new_id
            self.datos[self.current_selected_theme].append(new_note_dict)
            self._refresh_notes_view(select_last=True)

    def delete_note(self):
        """
        Elimina una nota seleccionada.

        Abre una ventana de diálogo para confirmar la eliminación de la nota.
        Si se selecciona "Sí", elimina la nota en la base de datos y refresca la vista de las notas.
        Si la nota es una imagen, elimina el archivo de la imagen también.
        """
        note_id = self._get_selected_note_id()
        if not note_id: return

        note_to_delete = self._get_note_by_id(note_id)
        if not note_to_delete: return

        if messagebox.askyesno("Confirmar", f"¿Eliminar apunte '{note_to_delete['titulo']}'?"):
            if note_to_delete.get("type") == "image" and note_to_delete.get("path"):
                try:
                    if os.path.exists(note_to_delete["path"]): os.remove(note_to_delete["path"])
                except OSError as e: print(f"Error al eliminar archivo de imagen: {e}")

            sat_id = f"{self.current_selected_theme}_{note_id}"
            if sat_id in self.open_satellites:
                self.open_satellites.pop(sat_id).destroy()

            self.data_manager.delete_note(note_id)
            self.datos[self.current_selected_theme] = [n for n in self.datos[self.current_selected_theme] if n['id'] != note_id]
            self._refresh_notes_view()

    def rename_note(self):
        """
        Renombra una nota seleccionada.

        Abre una ventana de diálogo para ingresar el nuevo título de la nota.
        Si el título es válido, actualiza la nota en la base de datos y refresca la vista de las notas.
        """

        note_id = self._get_selected_note_id()
        if not note_id:
            messagebox.showwarning("Atención", "Selecciona una nota para renombrar.")
            return

        note_to_rename = self._get_note_by_id(note_id)
        if not note_to_rename: return

        old_title = note_to_rename["titulo"]
        new_title_str = CustomInputDialog(self.root, "Renombrar Nota", "Nuevo título:", old_title, self.font_normal).show()

        if new_title_str and new_title_str.strip() and new_title_str.strip() != old_title:
            clean_title = new_title_str.strip()
            note_to_rename["titulo"] = clean_title
            self.data_manager.update_note(note_id, note_to_rename)
            self._refresh_notes_view()

            sat_id = f"{self.current_selected_theme}_{note_id}"
            if sat_id in self.open_satellites and hasattr(self.open_satellites[sat_id], 'title_label'):
                self.open_satellites[sat_id].title_label.config(text=clean_title)

    def open_note_editor(self, event=None):
        """
        Abre una ventana emergente para editar una nota de texto.

        Primero se selecciona una nota en la lista de apuntes y se la pasa a
        esta función. Luego se crea una ventana emergente en la que se inserta
        un widget de texto con el contenido de la nota. La ventana emergente
        tiene un botón "Guardar y Cerrar" que guarda los cambios hechos en la
        nota y la cierra.
        """

        note_id = self._get_selected_note_id()
        if not note_id: return

        note_data = self._get_note_by_id(note_id)
        if not note_data or note_data.get("type") == "image": return

        editor = tk.Toplevel(self.root)
        if platform.system() == "Windows" and pywinstyles: pywinstyles.apply_style(editor, "acrylic")
        editor.title(f"Editando: {note_data['titulo']}")
        editor.geometry("600x500")

        text_widget = tk.Text(editor, font=self.font_editor, wrap='word', bd=0, highlightthickness=0, relief="flat", padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert("1.0", note_data.get("contenido", ""))

        def save_and_close():
            """
            Cierra la ventana emergente del editor de notas y guarda los cambios hechos en la nota.

            Primero se actualiza el contenido de la nota con el texto ingresado en el widget de texto.
            Luego se elimina la ventana emergente y se recrea la ventana satélite asociada a la nota, si la hay.
            """

            note_data["contenido"] = text_widget.get("1.0", tk.END).strip()
            self.data_manager.update_note(note_data['id'], note_data)

            sat_id = f"{self.current_selected_theme}_{note_data['id']}"
            if sat_id in self.open_satellites:
                self.open_satellites.pop(sat_id).destroy()
                self._recreate_satellite(self.current_selected_theme, note_data['id'])

            editor.destroy()

        editor.protocol("WM_DELETE_WINDOW", save_and_close)
        tk.ttk.Button(editor, text="Guardar y Cerrar", command=save_and_close, style="Accent.TButton").pack(pady=10)

    def toggle_pin_note(self, event=None, note_id=None, theme=None):
        """
        Ancla o desancla una nota. Esta función es flexible y está diseñada para
        funcionar en dos escenarios diferentes:

        1.  Cuando se llama sin argumentos (desde la UI principal, a través de un
            evento o un botón), opera sobre la nota que está actualmente seleccionada
            en la `listbox` de apuntes.

        2.  Cuando se le pasa un `note_id` y un `theme` (llamada desde el botón '✖'
            de una ventana satélite), opera directamente sobre esa nota específica,
            sin importar la selección actual en la UI principal.
        """

        # Determina sobre qué tema se va a operar.
        theme_to_use = self.current_selected_theme

        # Escenario 2: La llamada viene de un satélite.
        if note_id is not None and theme is not None:
            theme_to_use = theme
        # Escenario 1: La llamada viene de la UI principal.
        else:
            note_id = self._get_selected_note_id()

        # Comprobación de seguridad: Si no tenemos un ID de nota o un tema válido,
        # no podemos continuar.
        if not note_id or not theme_to_use:
            return

        # Buscamos la nota correspondiente en nuestra estructura de datos en memoria.
        # Es crucial operar sobre la versión en RAM para mantener la consistencia de la UI.
        # Usamos un bucle explícito en lugar de _get_note_by_id para manejar el caso
        # en que el 'theme_to_use' no sea el 'current_selected_theme'.
        note_data = None
        for note in self.datos.get(theme_to_use, []):
            if note['id'] == note_id:
                note_data = note
                break

        # Si, por alguna razón, la nota no se encuentra, abortamos para evitar errores.
        if not note_data:
            return

        # El núcleo de la lógica: invertimos el estado 'anclado' de la nota.
        # El .get('anclado', False) previene un error si la clave no existiera.
        note_data["anclado"] = not note_data.get("anclado", False)

        # Persistimos el cambio en la base de datos. Esta es la operación crítica.
        # Le pasamos el ID y el diccionario de la nota completo y actualizado.
        self.data_manager.update_note(note_id, note_data)

        # Finalmente, le decimos a la lógica de la UI que muestre u oculte la ventana
        # satélite según el nuevo estado de 'anclado'.
        self._handle_satellite_toggle(theme_to_use, note_id, note_data["anclado"])

    def _handle_satellite_toggle(self, theme, note_id, should_be_pinned):
        """
        Maneja el toggle de una nota satélite. Si should_be_pinned es True, intenta abrir la nota
        satélite si no lo está ya. Si es False, intenta cerrar la ventana satélite si
        existe. El parámetro 'theme' es el nombre del tema al que pertenece la nota.
        El parámetro 'note_id' es el ID único de la nota.
        """
        sat_id = f"{theme}_{note_id}"
        if should_be_pinned:
            if sat_id not in self.open_satellites:
                self._recreate_satellite(theme, note_id)
        elif sat_id in self.open_satellites:
            self.open_satellites.pop(sat_id).destroy()

    def _recreate_satellite(self, theme, note_id):

        """
        Vuelve a crear una ventana satélite para una nota después de que ha cambiado
        su estado de 'anclado'.

        :param theme: El tema al que pertenece la nota.
        :param note_id: El ID de la nota que se va a recrear.
        :return: None
        """
        note_index = next((i for i, note in enumerate(self.datos[theme]) if note['id'] == note_id), None)
        if note_index is not None:
            self.satellite_manager.create_satellite_window(theme, note_index)

    def add_new_theme(self):
        """Abre un diálogo para solicitar el nombre de un nuevo tema.
        Si el nombre no está vacío, se crea el tema y se agrega a la lista de temas.
        Si el tema ya existe, se muestra un mensaje de advertencia."""
        name = CustomInputDialog(self.root, "Nuevo Tema", "Nombre del nuevo tema:", font_normal=self.font_normal).show()
        if name and name.strip():
            clean_name = name.strip()
            if clean_name in self.datos:
                messagebox.showwarning("Atención", f"El tema '{clean_name}' ya existe.")
            elif self.data_manager.add_theme(clean_name):
                self.datos[clean_name] = []
                self.populate_themes_list()
                for i, item in enumerate(self.listbox_temas.get(0, tk.END)):
                    if item == clean_name:
                        self.listbox_temas.selection_set(i)
                        self.listbox_temas.event_generate("<<ListboxSelect>>")
                        break

    def rename_theme(self):
        """
        Renombra un tema existente.

        Pide una interfaz de diálogo para que el usuario escriba el nuevo nombre del tema.
        Luego, actualiza la base de datos y la lista de temas.

        Si el usuario no selecciona un tema, muestra un mensaje de advertencia.
        Si el usuario introduce un nombre que ya existe, muestra un mensaje de advertencia.
        """
        if not self.current_selected_theme:
            messagebox.showwarning("Atención", "Selecciona un tema para renombrar.")
            return

        old_name = self.current_selected_theme
        new_name_str = CustomInputDialog(self.root, "Renombrar Tema", "Nuevo nombre para el tema:", old_name, self.font_normal).show()

        if new_name_str and new_name_str.strip() and new_name_str.strip() != old_name:
            clean_name = new_name_str.strip()
            if clean_name in self.datos:
                messagebox.showwarning("Atención", f"El tema '{clean_name}' ya existe.")
                return

            self.data_manager.rename_theme(old_name, clean_name)
            self.datos[clean_name] = self.datos.pop(old_name)
            self.current_selected_theme = clean_name
            self.populate_themes_list()

    def delete_theme(self):
        """
        Elimina un tema y todas sus notas asociadas. Si se selecciona
        "Sí", se eliminarán todos los datos asociados al tema seleccionado.
        Si se selecciona "No", no se realizará ninguna acción.
        """

        if not self.current_selected_theme:
            messagebox.showwarning("Atención", "Selecciona un tema para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{self.current_selected_theme}' y todas sus notas? Esta acción es irreversible."):
            notes_to_delete = self.datos.get(self.current_selected_theme, [])
            for note in notes_to_delete:
                if note.get("type") == "image" and note.get("path"):
                    try:
                        if os.path.exists(note["path"]): os.remove(note["path"])
                    except OSError as e: print(f"Error al eliminar archivo de imagen: {e}")

            self.data_manager.delete_theme(self.current_selected_theme)
            del self.datos[self.current_selected_theme]
            self.current_selected_theme = None
            self.populate_themes_list()
            self._refresh_notes_view()

    def populate_themes_list(self):
        """
        Rellena la lista de temas en la interfaz de usuario. La lista se
        ordena alfabticamente y se selecciona el tema actual si es
        necesario.
        """
        current_selection = self.current_selected_theme
        self.listbox_temas.delete(0, tk.END)
        sorted_themes = sorted(self.datos.keys())
        for i, tema in enumerate(sorted_themes):
            self.listbox_temas.insert(tk.END, tema)
            if tema == current_selection:
                self.listbox_temas.selection_set(i)

    def toggle_sidebar(self):
        """
        Toggle the sidebar visibility.

        If the sidebar is visible, it hides the sidebar and shows the toggle frame.
        If the sidebar is not visible, it shows the sidebar and hides the toggle frame.
        """
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar_toggle_frame.pack_forget()
            self.sidebar.pack(side='left', fill='y', padx=(5,0), pady=5)
        else:
            self.sidebar.pack_forget()
            self.sidebar_toggle_frame.pack(side='left', fill='y', padx=(5,0), pady=5)

    def toggle_theme(self):
        """
        Toggle the theme of the application between light and dark.

        This function also re-renders all open satellites with the new theme.
        """
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        sv_ttk.set_theme(self.current_theme)
        self.style_listboxes()
        for sat_id, sat_window in list(self.open_satellites.items()):
            theme, note_id_str = sat_id.split('_', 1)
            note_id = int(note_id_str)
            sat_window.destroy()
            self.open_satellites.pop(sat_id)
            self._recreate_satellite(theme, note_id)

    def style_listboxes(self):
        """
        Cambia el estilo de las listas de temas y apuntes para que
        se ajusten al tema actual (oscuro o claro).
        """
        bg, fg, sel_bg = ("#2b2b2b", "white", "#0078d4") if self.current_theme == "dark" else ("#f3f3f3", "black", "#3399ff")
        self.listbox_temas.config(background=bg, foreground=fg, selectbackground=sel_bg, selectforeground="white")
        self.listbox_apuntes.config(background=bg, foreground=fg, selectbackground=sel_bg, selectforeground="white")

    def clear_search(self):
        """
        Limpia la barra de búsqueda y vuelve a mostrar todas las notas
        en la lista de apuntes.
        """
        self.search_var.set("")
        self._refresh_notes_view()
