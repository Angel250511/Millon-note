# ui_components.py
# Módulo que contiene componentes de UI personalizados y reutilizables.
# Estos componentes están desacoplados de la lógica de la aplicación principal.

import tkinter as tk
from tkinter import ttk
import platform

# Intenta importar pywinstyles si está disponible, pero no hagas que sea un requisito estricto.
try:
    import pywinstyles
except ImportError:
    pywinstyles = None

# ---- CLASE PARA LA SCROLLBAR -
class CustomScrollbar(tk.Canvas):
    def __init__(self, parent, command, **kwargs):
        self.troughcolor = kwargs.pop('troughcolor', '#F0F0F0')
        self.thumbcolor = kwargs.pop('thumbcolor', '#C0C0C0')
        self.hovercolor = kwargs.pop('hovercolor', '#A0A0A0')
        
        super().__init__(parent, width=12, highlightthickness=0, bg=self.troughcolor, **kwargs)
        
        self.command = command
        self.bind('<Configure>', self._draw_thumb)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

        self.thumb = self.create_rectangle(0, 0, 0, 0, fill=self.thumbcolor, outline="")
        self.scroll_lo = 0.0
        self.scroll_hi = 1.0
        
        self.start_y = 0
        self.start_fraction = 0.0

    def set(self, lo, hi):
        self.scroll_lo, self.scroll_hi = float(lo), float(hi)
        if self.scroll_lo <= 0.0 and self.scroll_hi >= 1.0:
            if self.winfo_ismapped(): self.pack_forget()
        else:
            if not self.winfo_ismapped(): self.pack(side="right", fill="y")
        self._draw_thumb()

    def get(self):
        return (self.scroll_lo, self.scroll_hi)

    def _draw_thumb(self, event=None):
        self.delete(self.thumb)
        if self.scroll_hi - self.scroll_lo < 1:
            canvas_height = self.winfo_height()
            thumb_height = max(10, (self.scroll_hi - self.scroll_lo) * canvas_height)
            thumb_y = self.scroll_lo * canvas_height
            self.thumb = self.create_rectangle(2, thumb_y, 10, thumb_y + thumb_height, fill=self.thumbcolor, outline="")

    def _on_enter(self, event=None):
        self.itemconfig(self.thumb, fill=self.hovercolor)

    def _on_leave(self, event=None):
        self.itemconfig(self.thumb, fill=self.thumbcolor)

    def _on_press(self, event):
        thumb_coords = self.coords(self.thumb)
        if len(thumb_coords) > 1 and thumb_coords[1] <= event.y <= thumb_coords[3]:
            self.start_y = event.y
            self.start_fraction = self.scroll_lo
        else:
            if self.command:
                if event.y < (thumb_coords[1] if len(thumb_coords) > 1 else 0):
                    self.command('scroll', -1, 'pages')
                else:
                    self.command('scroll', 1, 'pages')
    
    def _on_drag(self, event):
        if self.winfo_height() > 0:
            delta_fraction = (event.y - self.start_y) / self.winfo_height()
            new_fraction = self.start_fraction + delta_fraction
            new_fraction = max(0.0, min(new_fraction, 1.0 - (self.scroll_hi - self.scroll_lo)))
            if self.command:
                self.command('moveto', new_fraction)

# ---- DIÁLOGOS PERSONALIZADOS (ESTILO FLUENT) ----
class CustomInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, initial_value="", font_normal=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set(); self.title(title); self.result = None; self.resizable(False, False)
        if platform.system() == "Windows" and pywinstyles:
            pywinstyles.apply_style(self, "acrylic")
        main_frame = ttk.Frame(self, padding=20); main_frame.pack(expand=True, fill="both")
        ttk.Label(main_frame, text=prompt, font=font_normal).pack(pady=(0, 10), anchor="w")
        self.entry = ttk.Entry(main_frame, font=font_normal, width=40); self.entry.pack(pady=(0, 15), fill="x", ipady=2)
        self.entry.insert(0, initial_value); self.entry.focus_set(); self.entry.bind("<Return>", self._on_ok)
        buttons_frame = ttk.Frame(main_frame); buttons_frame.pack(fill="x")
        ok_button = ttk.Button(buttons_frame, text="Aceptar", command=self._on_ok, style="Accent.TButton"); ok_button.pack(side="right")
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", command=self._on_cancel); cancel_button.pack(side="right", padx=(0, 5))
    def _on_ok(self, event=None): self.result = self.entry.get(); self.destroy()
    def _on_cancel(self): self.result = None; self.destroy()
    def show(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}"); self.wait_window(); return self.result

class ColorPickerDialog(tk.Toplevel):
    def __init__(self, parent, colors, font_normal=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set(); self.title("Elige un Color"); self.result = None; self.resizable(False, False)
        if platform.system() == "Windows" and pywinstyles:
            pywinstyles.apply_style(self, "acrylic")
        main_frame = ttk.Frame(self, padding=20); main_frame.pack(expand=True, fill="both")
        ttk.Label(main_frame, text="Selecciona el color de la nota:", font=font_normal).pack(pady=(0, 15))
        colors_frame = ttk.Frame(main_frame); colors_frame.pack()
        style = ttk.Style()
        for name, hex_code in colors.items():
            style_name = f'{name.replace(" ", "")}.TButton'
            style.configure(style_name, background=hex_code, foreground='black', borderwidth=1, relief='flat', font=font_normal)
            style.map(style_name, background=[('active', '#ffffff'), ('pressed', '#dddddd')], relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
            btn = ttk.Button(colors_frame, text=name, style=style_name, command=lambda c=hex_code: self.on_color_select(c)); btn.pack(pady=4, padx=10, fill='x', ipady=5)
    def on_color_select(self, color_hex): self.result = color_hex; self.destroy()
    def show(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}"); self.wait_window(); return self.result