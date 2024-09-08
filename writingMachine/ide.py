import tkinter as tk
from tkinter import *


def init_ide():
    # Crear la ventana principal
    window = tk.Tk()
    window.title("Champi")
    window.geometry("1000x800")

    icon = tk.PhotoImage(file="icon.png")
    window.iconphoto(False, icon)

    # Crear paned window para dividir la ventana en dos secciones
    paned_main = tk.PanedWindow(window, orient=tk.VERTICAL, sashwidth=5, bg="gray")  # Panel principal (vertical)
    paned_main.pack(fill=tk.BOTH, expand=True)

    # Panel superior (izquierda y derecha)
    paned_top = tk.PanedWindow(paned_main, orient=tk.HORIZONTAL, sashwidth=5,
                               bg="gray")  # Panel superior (horizontal)

    # Crear frame para el panel izquierdo
    frame_left = tk.Frame(paned_top, bg="lightgray")
    frame_left.pack(fill=tk.BOTH, expand=True)

    # Crear scrollbar para el panel izquierdo
    scroll_left_y = tk.Scrollbar(frame_left)
    scroll_left_x = tk.Scrollbar(frame_left, orient=tk.HORIZONTAL)

    # Crear texto scrolleable en el panel izquierdo
    text_left = tk.Text(frame_left, wrap=tk.NONE,
                        yscrollcommand=lambda *args: update_scroll(scroll_left_y, text_left, 'y', *args),
                        xscrollcommand=lambda *args: update_scroll(scroll_left_x, text_left, 'x', *args), bg="gray50",
                        fg="black")
    text_left.pack(fill=tk.BOTH, expand=True)

    # Crear frame para el panel derecho (más pequeño)
    frame_right = tk.Frame(paned_top, bg="gray80")
    frame_right.pack(fill=tk.BOTH, expand=True)

    # Crear scrollbar para el panel derecho
    scroll_right_y = tk.Scrollbar(frame_right)
    scroll_right_x = tk.Scrollbar(frame_right, orient=tk.HORIZONTAL)

    # Crear texto scrolleable en el panel derecho
    # Crear el widget Text para los números de línea en el panel derecho
    # Números de línea en el panel derecho
    line_numbers_right = tk.Text(frame_right, width=4, bg="gray60", fg="black", state="disabled", font=("Consolas", 10),
                                 padx=5, pady=5, bd=0, relief=tk.FLAT)
    line_numbers_right.pack(side=tk.LEFT, fill=tk.Y)

    text_right = tk.Text(frame_right, wrap=tk.NONE, bg="gray60", fg="black", font=("Consolas", 10),
                         padx=5, pady=5, bd=0, relief=tk.FLAT,
                         yscrollcommand=lambda *args: [scroll_right_y.set(*args),
                                                       update_line_numbers(text_right, line_numbers_right)],
                         xscrollcommand=lambda *args: scroll_right_x.set(*args))

    text_right.pack(fill=tk.BOTH, expand=True)

    text_right.bind("<KeyRelease>", lambda event: update_line_numbers(text_right, line_numbers_right))
    text_right.bind("<MouseWheel>", lambda event: update_line_numbers(text_right, line_numbers_right))

    # Añadir los frames superiores al paned window superior
    paned_top.add(frame_left, stretch="always")
    paned_top.add(frame_right, stretch="always")

    paned_top.paneconfig(frame_left, width=300)  # Panel izquierdo tendrá 600 píxeles de ancho
    paned_top.paneconfig(frame_right, width=700)

    # Añadir el paned superior al principal
    paned_main.add(paned_top, stretch="always")

    # Crear frame para el panel inferior (terminal)
    frame_terminal = tk.Frame(paned_main, bg="gray70")
    frame_terminal.pack(fill=tk.BOTH, expand=True)

    # Crear scrollbar para el panel inferior (terminal)
    scroll_terminal_y = tk.Scrollbar(frame_terminal)

    # Crear texto scrolleable en el panel inferior (terminal)
    text_terminal = tk.Text(frame_terminal, wrap=tk.NONE,
                            yscrollcommand=lambda *args: update_scroll(scroll_terminal_y, text_terminal, 'y', *args),
                            bg="gray30", fg="black")
    text_terminal.pack(fill=tk.BOTH, expand=True)

    # Añadir el frame inferior al paned window principal
    paned_main.add(frame_terminal, stretch="always")
    paned_main.paneconfig(frame_terminal, height=200)

    # Iniciar el loop de la ventana
    window.mainloop()


def update_scroll(scroll, widget, axis, *args):
    # Si es el eje y, configuramos el scroll para el texto
    if axis == 'y':
        scroll.set(*args)
        widget.update_idletasks()  # Actualiza la visualización del widget
        widget.yview_moveto(args[0])  # Actualiza la vista

    # Si es el eje x, configuramos el scroll horizontal
    elif axis == 'x':
        scroll.set(*args)
        widget.update_idletasks()  # Actualiza la visualización del widget
        widget.xview_moveto(args[0])  # Actualiza la vista

    # No es necesario configurar scrollregion para Text widgets.


def update_line_numbers(text_widget, line_numbers_widget):
    line_numbers_widget.config(state="normal")
    line_numbers_widget.delete("1.0", "end")

    # Obtener el número de líneas en el widget de texto
    line_count = int(text_widget.index('end').split('.')[0])

    # Insertar números de línea de manera alineada con el texto
    for i in range(1, line_count):
        line_numbers_widget.insert(f"{i}.0", f"{i:>2}  \n")  # Ajusta el formato de los números de línea

    line_numbers_widget.config(state="disabled")
