import tkinter as tk
from tkinter import messagebox, ttk

class VariableContext:
    def __init__(self):
        self.variables = {}
        self.current_procedure = None

    def set_variable(self, var_name, value, var_type):
        self.variables[var_name] = {
            "value": value,
            "type": var_type,
            "procedure": self.current_procedure
        }

    def get_variable(self, var_name):
        return self.variables.get(var_name, {}).get("value")

    def get_variable_type(self, var_name):
        return self.variables.get(var_name, {}).get("type")

    def get_variable_procedure(self, var_name):
        return self.variables.get(var_name, {}).get("procedure")

    def remove_variable(self, var_name):
        if var_name in self.variables:
            del self.variables[var_name]

    def set_current_procedure(self, procedure_name):
        self.current_procedure = procedure_name

    def clear_current_procedure(self):
        self.current_procedure = None

    def print_symbol_table(self):
        print("Symbol Table:")
        print("{:<10} {:<10} {:<15} {}".format("Name", "Type", "Procedure", "Value"))
        print("-" * 50)
        for name, info in self.variables.items():
            proc = info['procedure'] if info['procedure'] else "Global"
            print("{:<10} {:<10} {:<15} {}".format(name, info['type'], proc, info['value']))
        self.show_symbol_table_gui()

    def show_symbol_table_gui(self):
        symbol_window = tk.Toplevel()
        symbol_window.title("Symbol Table")
        symbol_window.geometry("500x300")

        tree = ttk.Treeview(symbol_window, columns=("Name", "Type", "Procedure", "Value"), show='headings', height=12)
        tree.heading("Name", text="Name")
        tree.heading("Type", text="Type")
        tree.heading("Procedure", text="Procedure")
        tree.heading("Value", text="Value")
        tree.column("Name", anchor="center", width=100)
        tree.column("Type", anchor="center", width=100)
        tree.column("Procedure", anchor="center", width=150)
        tree.column("Value", anchor="center", width=100)

        for name, info in self.variables.items():
            proc = info['procedure'] if info['procedure'] else "Global"
            tree.insert("", "end", values=(name, info['type'], proc, info['value']))

        scrollbar = ttk.Scrollbar(symbol_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)