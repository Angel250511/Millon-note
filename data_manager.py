# data_manager.py (Versión 3.0 - Nativa de SQLite)
# Módulo de persistencia de datos que gestiona todas las interacciones con la base de datos SQLite.
import sqlite3

class DataManager:
    def __init__(self, db_file):
        """Inicializa el gestor de datos y establece la conexión a la base de datos."""
        self.DATA_FILE = db_file
        self.conn = sqlite3.connect(self.DATA_FILE)
        self.conn.row_factory = sqlite3.Row
        self._initialize_db() # Se asegura de que las tablas existan en cada arranque.

    def _initialize_db(self):
        """Crea las tablas de la base de datos si no existen.
        También verifica si la base de datos está completamente vacía para añadir datos de bienvenida.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                path TEXT,
                pinned BOOLEAN NOT NULL,
                pos_x INTEGER,
                pos_y INTEGER,
                color TEXT,
                width INTEGER,
                FOREIGN KEY (theme_id) REFERENCES themes (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

        # NUEVA LÓGICA: Si la base de datos está vacía, la poblamos.
        cursor.execute("SELECT COUNT(id) FROM themes")
        if cursor.fetchone()[0] == 0:
            self._create_welcome_data()

    def _create_welcome_data(self):
        """Inserta los datos de bienvenida en una base de datos vacía."""
        print("Base de datos vacía detectada. Creando datos de bienvenida...")
        welcome_theme_name = "Nexus Notes"
        self.add_theme(welcome_theme_name) # Llama a su propio método para añadir el tema
        
        welcome_note = {
            "titulo": "¡Bienvenido a Nexus Notes!", "type": "text", 
            "contenido": "Esta es una nota de bienvenida.\nPuedes editarla o borrarla.", 
            "anclado": False, "pos_x": 100, "pos_y": 100, "color": "#FFFFA5"
        }
        self.add_note(welcome_theme_name, welcome_note) # Y la nota de bienvenida
        print("Datos de bienvenida creados.")


    def load_data(self):
        """Carga todos los datos desde la DB y los reconstruye en el formato que la app espera."""
        app_data = {}
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM themes ORDER BY name")
        themes = cursor.fetchall()

        for theme in themes:
            theme_name = theme['name']
            app_data[theme_name] = []
            
            cursor.execute('''
                SELECT * FROM notes WHERE theme_id = ? ORDER BY id
            ''', (theme['id'],))
            notes = cursor.fetchall()

            for note in notes:
                note_dict = {
                    "id": note['id'],
                    "titulo": note['title'],
                    "type": note['type'],
                    "contenido": note['content'],
                    "path": note['path'],
                    "anclado": bool(note['pinned']),
                    "pos_x": note['pos_x'],
                    "pos_y": note['pos_y'],
                    "color": note['color'],
                    "width": note['width']
                }
                app_data[theme_name].append(note_dict)
        
        # La configuración sigue siendo simple, no necesita base de datos por ahora.
        default_settings = {"theme": "dark", "sidebar_visible": True}
        return app_data, default_settings

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    # --- Métodos de escritura (CRUD: Create, Read, Update, Delete) ---
    # Estos métodos ya están bien y no necesitan cambios.
    # Son la API interna para interactuar con la base de datos.
    
    def add_theme(self, theme_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO themes (name) VALUES (?)", (theme_name,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return None

    def add_note(self, theme_name, note_dict):
        """
        Agrega una nota a la base de datos.

        :param theme_name: El nombre del tema al que pertenece la nota.
        :param note_dict: Un diccionario que contiene los datos de la nota.
        :return: El ID de la nota recién agregada, o None si no se pudo agregar.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM themes WHERE name = ?", (theme_name,))
        theme_row = cursor.fetchone()
        if not theme_row:
            return None
        theme_id = theme_row['id']

        cursor.execute('''
            INSERT INTO notes (theme_id, title, type, content, path, pinned, pos_x, pos_y, color, width)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            theme_id,
            note_dict.get('titulo'),
            note_dict.get('type'),
            note_dict.get('contenido'),
            note_dict.get('path'),
            note_dict.get('anclado', False),
            note_dict.get('pos_x'),
            note_dict.get('pos_y'),
            note_dict.get('color'),
            note_dict.get('width')
        ))
        self.conn.commit()
        return cursor.lastrowid

    def update_note(self, note_id, note_dict):
        """Actualiza una nota existente usando su ID único."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE notes SET
                title = ?, content = ?, path = ?, pinned = ?, pos_x = ?, pos_y = ?, color = ?, width = ?
            WHERE id = ?
        ''', (
            note_dict.get('titulo'),
            note_dict.get('contenido'),
            note_dict.get('path'),
            note_dict.get('anclado', False),
            note_dict.get('pos_x'),
            note_dict.get('pos_y'),
            note_dict.get('color'),
            note_dict.get('width'),
            note_id
        ))
        self.conn.commit()
        
    def delete_note(self, note_id):
        """
        Elimina una nota de la base de datos.

        Parámetros:
            note_id (int): El ID único de la nota a eliminar.
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()

    def delete_theme(self, theme_name):
        """
        Elimina un tema de la base de datos.

        Parámetros:
            theme_name (str): El nombre del tema a eliminar.

        Devuelve:
            None
        """

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM themes WHERE name = ?", (theme_name,))
        self.conn.commit()
        
    def rename_theme(self, old_name, new_name):
        """
        Renombra un tema existente.

        old_name: str - El nombre actual del tema.
        new_name: str - El nuevo nombre para el tema.

        Actualiza la base de datos con el nuevo nombre del tema.
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE themes SET name = ? WHERE name = ?", (new_name, old_name))
        self.conn.commit()