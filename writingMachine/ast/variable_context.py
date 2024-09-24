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