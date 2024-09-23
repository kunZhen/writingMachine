class VariableContext:
    def __init__(self):
        self.variables = {}

    def set_variable(self, var_name, value):
        self.variables[var_name] = value

    def get_variable(self, var_name):
        return self.variables.get(var_name, None)  # Devuelve None si no está definido

    def remove_variable(self, var_name):
        if var_name in self.variables:
            del self.variables[var_name]
