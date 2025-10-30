# config.py
# Módulo para almacenar todas las constantes y configuraciones de la aplicación.
# Centralizar estos valores facilita la modificación y el mantenimiento.

# --- Rutas y Archivos ---
DATA_FILE = "Millon_note.db"
IMAGE_DIR = "MNI"

# --- Iconografía ---
# Usamos un diccionario para que sea fácil añadir o cambiar iconos sin tocar la lógica.
ICONS = {
    "add": "\uE710", 
    "image": "\uE91B", 
    "rename": "\uE70F", 
    "delete": "\uE74D", 
    "pin": "\uE718", 
    "theme": "\uE790", 
    "show_sidebar": "\uE700", 
    "hide_sidebar": "\uE72B"
}

# --- Paleta de Colores ---
# Colores predefinidos para las notas tipo post-it.
POSTIT_COLORS = {
    "Amarillo Clásico": "#FFFFA5", 
    "Rosa Pálido": "#FFD1DC", 
    "Azul Cielo": "#AEC6CF", 
    "Verde Menta": "#C1E1C1", 
    "Naranja Suave": "#FFDAB9", 
    "Lila": "#E6E6FA"
}