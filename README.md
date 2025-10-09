# 📘 Nexus Notes – Sistema Inteligente de Notas Flotantes Asistido por IA

## 1. Introducción General

**Nexus Notes** es una aplicación de escritorio desarrollada en entorno **Tkinter (Python GUI Toolkit)** y codificada mediante un proceso de **colaboración humano–IA**, utilizando **Google AI Studio** como sistema generativo de ingeniería de código.  
El proyecto representa un ejemplo de **codificación artificial aplicada**: una metodología donde la inteligencia artificial produce el código base, mientras el humano actúa como **mentor conceptual**, definiendo requerimientos, arquitectura y comportamiento lógico del software.

El resultado es una **plataforma de notas flotantes inteligentes**, diseñada para personas con déficit de atención, profesionales multitarea o usuarios que requieren mantener múltiples notas visibles simultáneamente, sin distracciones ni interferencias en el flujo de trabajo.

---

## 2. Descripción Técnica General

**Tipo de Proyecto:** Aplicación de escritorio (Standalone).  
**Lenguaje Base:** Python 3.x (para desarrollo).  
**Entorno de Ejecución Final:** Archivo ejecutable (.exe) distribuible sin dependencias externas.  
**Interfaz:** Gráfica (GUI) basada en `tkinter` con componentes de interacción visual dinámica.  
**Motor de Persistencia:** Sistema JSON local (archivo `nexus_notes_data.json`).  
**Generación de Código:** IA generativa (Google AI Studio) bajo supervisión humana directa.  
**Modo de distribución:** Instalación directa mediante ejecutable empaquetado con PyInstaller u otro generador de binarios.

---

## 3. Propósito e Innovación

El propósito de **Nexus Notes** es simplificar la **gestión cognitiva y visual de información breve** mediante un sistema de notas flotantes “anclables” en pantalla, simulando post-its digitales pero con comportamientos inteligentes:
- Persistencia automática del contenido.
- Posicionamiento recordado en pantalla.
- Capacidad de flotar sobre todas las ventanas.
- Soporte para fórmulas matemáticas renderizadas en tiempo real (usando `matplotlib`).
- Adaptación visual realista a escala física (3x3 pulgadas reales según DPI del monitor).
- Interacción intuitiva basada en eventos del sistema de ventanas.

Su enfoque está orientado a la **productividad cognitiva**: reforzar la memoria de trabajo mediante estimulación visual controlada y minimizar la interferencia entre tareas.

---

## 4. Arquitectura de Software

### 4.1. Estructura de Capas

| Capa | Descripción | Principales Componentes |
|------|--------------|-------------------------|
| **Capa de Presentación (UI)** | Implementa la interfaz gráfica, gestión de eventos y manipulación de ventanas flotantes. | `tkinter`, `font`, `Toplevel`, `Frame`, `Scrollbar`, `Listbox` |
| **Capa de Lógica de Negocio** | Controla la creación, edición, anclaje y persistencia de notas. Coordina los flujos entre interfaz y almacenamiento. | `add_new_note`, `toggle_pin_note`, `create_satellite_window`, `delete_theme` |
| **Capa de Persistencia** | Gestiona la lectura y escritura de datos persistentes en formato JSON. | `load_data`, `write_data_to_disk` |
| **Capa de Renderizado Matemático** | Genera visualizaciones y fórmulas matemáticas incrustadas en las notas. | `matplotlib`, `io.BytesIO`, `PIL.Image`, `ImageTk.PhotoImage` |
| **Capa de Control Principal (Main App)** | Punto de inicio y ciclo de vida del programa. | `root.mainloop()`, gestión de cierre y guardado |

---

## 5. Diseño Funcional

### 5.1. Temas y Categorías
Cada grupo de notas pertenece a un “tema” (por ejemplo, *Realista*, *Ideas rápidas*, *Recordatorios diarios*).  
El usuario puede **crear, eliminar o renombrar temas**. Cada tema agrupa múltiples apuntes, manteniendo una jerarquía lógica.

### 5.2. Notas flotantes (Post-its virtuales)
Cada nota puede ser:
- **Anclada**: visible como ventana flotante permanente (se conserva su posición exacta en pantalla).
- **Desanclada**: almacenada en la base JSON pero no visible.
- **Editable**: el usuario puede modificar el contenido desde el editor integrado.

### 5.3. Persistencia inteligente
Al cerrar la aplicación, todas las notas, posiciones, estados de anclaje y temas son guardados en `nexus_notes_data.json` de manera automática.  
El formato JSON facilita portabilidad, respaldo y edición manual si se requiere.

### 5.4. Compatibilidad visual realista
Los tamaños de las notas son equivalentes a **3x3 pulgadas reales**, calculadas dinámicamente según la densidad de píxeles del monitor (DPI).  
Esto produce una experiencia táctil y visual idéntica a las notas adhesivas físicas.

---

## 6. Descripción Detallada de Componentes

### 6.1. Módulo `load_data()`
- Verifica la existencia del archivo de datos JSON.
- Si no existe, crea una estructura inicial predeterminada.
- Implementa manejo de errores ante archivos corruptos o no encontrados.

### 6.2. Módulo `write_data_to_disk()`
- Guarda todos los cambios de notas, temas y posiciones.
- Emplea manejo de excepciones controladas para evitar pérdida de información.

### 6.3. Función `create_satellite_window()`
- Crea la ventana flotante “post-it”.
- Define color, tamaño, scroll y renderizado de texto.
- Implementa arrastre libre en pantalla y guardado de posición.
- Gestiona el cierre individual de cada nota anclada.

### 6.4. Función `open_note_editor()`
- Genera un editor modal para modificar contenido de la nota.
- Guarda automáticamente al cerrar la ventana.
- Regenera la versión flotante actualizada si estaba anclada.

### 6.5. Funciones de Control (`add_new_note`, `delete_note`, `toggle_pin_note`)
- Controlan la creación, eliminación y anclaje de notas.
- Sincronizan el estado visual con la base de datos persistente.

---

## 7. Flujo de Ejecución

1. **Inicio de la Aplicación**
   - Se carga el archivo JSON existente o se inicializa uno nuevo.
   - Se crean los paneles principales (temas y apuntes).
2. **Interacción del Usuario**
   - Selección de tema → muestra sus notas asociadas.
   - Doble clic en una nota → abre editor.
   - Clic en 📌 → convierte la nota en ventana flotante.
3. **Persistencia Continua**
   - Cada acción que modifica el estado es registrada inmediatamente.
   - Al cerrar, se ejecuta `on_close()` que guarda y finaliza el proceso.
4. **Reinicio**
   - En la siguiente sesión, se restauran las posiciones flotantes y temas previos.

---

## 8. Seguridad y Confiabilidad

- No se utilizan conexiones externas ni acceso a internet.
- El sistema opera completamente en entorno local (modo offline).
- El formato de guardado JSON evita corrupción masiva ante fallos inesperados.
- Se aplican validaciones de nombres duplicados y manejo de excepciones en operaciones críticas.

---

## 9. Optimización y Rendimiento

- Interfaz optimizada para bajo consumo de memoria.
- Uso controlado de `PIL` y `matplotlib` para renderizado ligero.
- Lógica asíncrona innecesaria eliminada para mejorar estabilidad.
- Gestión manual de DPI para evitar deformación visual en monitores de alta densidad.

---

## 10. Escalabilidad y Extensión

El diseño modular permite futuras expansiones, tales como:
- Integración con **voz a texto** o **reconocimiento de voz IA**.
- Sincronización en nube o almacenamiento cifrado.
- Implementación de recordatorios automáticos y alarmas.
- Exportación PDF o markdown de notas.
- Interfaz moderna (Fluent Design / Material UI) mediante frameworks de terceros.

---

## 11. Implementación Asistida por Inteligencia Artificial

El código fuente fue **generado y estructurado con asistencia de Google AI Studio**, dentro de un flujo de desarrollo denominado **Codificación Artificial Supervisada (CAS)**, donde:

- La IA redacta y organiza el código siguiendo directrices naturales del mentor humano.  
- El humano actúa como ingeniero supervisor, validando, corrigiendo y estructurando la lógica arquitectónica.  
- El resultado se alinea con las prácticas de **IA aplicada a ingeniería de software** (AI-driven Coding).

**Participación humana:**  
- Diseño conceptual del sistema.  
- Supervisión de la lógica de interfaz y persistencia.  
- Validación del comportamiento final y coherencia visual.  

**Participación de IA (Google AI Studio):**  
- Generación automática de código estructural.  
- Propuesta de soluciones de interacción gráfica.  
- Optimización sintáctica y corrección de errores.

Este modelo mixto demuestra la **capacidad de la IA moderna para impulsar el desarrollo de software autónomo con supervisión ética y técnica humana**, siendo aplicable a proyectos de ingeniería real.

---

## 12. Distribución y Entrega Final

La versión entregable al usuario final es un **ejecutable (.exe)** compilado a partir del código Python mediante herramientas como:
- `PyInstaller`
- `auto-py-to-exe`
- `cx_Freeze`

No requiere instalación de Python ni dependencias externas.
## 13. Compatibilidad del Sistema

| Sistema Operativo | Estado | Observaciones |
|-------------------|---------|----------------|
| Windows 10 / 11   | ✅ Estable | DPI ajustable y soporte completo |
| macOS             | ⚠️ Parcial | Requiere conversión con `py2app` |
| Linux (Ubuntu)    | ✅ | Compatible mediante empaquetado manual |

---

## 14. Mantenimiento y Actualizaciones

El mantenimiento del proyecto se recomienda bajo control de versiones (Git) con las siguientes pautas:

- **Versión inicial (v1.0.0):** Sistema funcional completo con persistencia local.  
- **Próximas versiones:**  
  - v1.1.0: Sincronización en la nube (opcional).  
  - v1.2.0: IA de resumen automático de notas.  
  - v2.0.0: Interfaz rediseñada en entorno multiplataforma.

---

## 15. Conclusión Técnica

**Nexus Notes** representa una síntesis entre ingeniería humana e inteligencia artificial aplicada, demostrando la capacidad de la IA para **co-escribir software estructurado, modular y funcional** en colaboración directa con el pensamiento humano.  
El proyecto se considera un caso de éxito en **codificación artificial aplicada a la productividad cognitiva**, evidenciando:

- Eficiencia en desarrollo asistido.  
- Integración coherente entre diseño y lógica.  
- Escalabilidad futura hacia entornos de IA híbrida.

---

## 16. Créditos y Autores

**Desarrollo conceptual y supervisión humana:**  
Ángel (Mentor Humano y Diseñador Cognitivo del Proyecto)

**Codificación generativa:**  
Google AI Studio (Sistema de Inteligencia Artificial de generación de código Python)

**Tecnologías utilizadas:**  
Tkinter, PIL (Pillow), Matplotlib, JSON, Python Standard Library.

---

## 17. Licencia

Este proyecto se entrega bajo **licencia de uso personal y demostrativa** para portafolio profesional.  
No está destinado a comercialización sin autorización explícita del autor.  
Todos los derechos reservados © 2025.

---

## 18. Contacto Profesional

**Autor:** Jesús Ángel Bustamante
**Propósito:** Demostración de ingeniería de software asistida por IA.  
**Aplicación:** Portafolio profesional y muestra de codificación artificial supervisada.  
**Correo de contacto:** *jarbustamante2025@gmail.com*  



