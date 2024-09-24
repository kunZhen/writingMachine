import tkinter as tk
from tkinter import messagebox, ttk


class VariableContext:
    def __init__(self):
        self.variables = {}

    def set_variable(self, var_name, value, var_type):
        self.variables[var_name] = {"value": value, "type": var_type}

    def get_variable(self, var_name):
        return self.variables.get(var_name, {}).get("value")

    def get_variable_type(self, var_name):
        return self.variables.get(var_name, {}).get("type")

    def remove_variable(self, var_name):
        if var_name in self.variables:
            del self.variables[var_name]

    def print_symbol_table(self):
        print("Symbol Table:")
        print("{:<10} {:<10} {}".format("Name", "Type", "Value"))
        print("-" * 40)
        for name, info in self.variables.items():
            print("{:<10} {:<10} {}".format(name, info['type'], info['value']))
        self.show_symbol_table_gui()  # Llamada a la función para mostrar en GUI

    def show_symbol_table_gui(self):
        # Crear una nueva ventana para la tabla de símbolos
        symbol_window = tk.Toplevel()  # Usa Toplevel para crear una ventana secundaria
        symbol_window.title("Symbol Table")
        symbol_window.geometry("300x200")  # Tamaño más pequeño

        # Crear un árbol (treeview) para mostrar la tabla
        tree = ttk.Treeview(symbol_window, columns=("Name", "Type", "Value"), show='headings', height=8)
        tree.heading("Name", text="Name")
        tree.heading("Type", text="Type")
        tree.heading("Value", text="Value")
        tree.column("Name", anchor="center", width=80)  # Ajustar el ancho de las columnas
        tree.column("Type", anchor="center", width=50)
        tree.column("Value", anchor="center", width=120)

        # Insertar los datos en el árbol
        for name, info in self.variables.items():
            tree.insert("", "end", iid=name, values=(name, info['type'], info['value']))

        # Agregar scrollbar
        scrollbar = tk.Scrollbar(symbol_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Empaquetar el árbol y scrollbar
        tree.pack(expand=True, fill=tk.BOTH)