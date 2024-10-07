class ProcedureVariableTracker:
    def __init__(self):
        self.procedures = {}  # {(procedure_name, param_count): {params: [], variables: []}}
        self.variables = {}   # {variable_name: [procedure_names]}

    def register_procedure(self, procedure_name, parameters):
        param_count = len(parameters)
        proc_key = (procedure_name, param_count)  # Clave única basada en el nombre y cantidad de parámetros

        if proc_key not in self.procedures:
            self.procedures[proc_key] = {"params": parameters, "variables": []}

        for param in parameters:
            self.register_variable(param, procedure_name)

    def get_procedure(self, procedure_name, param_count):
        proc_key = (procedure_name, param_count)
        return self.procedures.get(proc_key)

    def register_variable(self, variable_name, procedure_name):
        if variable_name not in self.variables:
            self.variables[variable_name] = []
        if procedure_name not in self.variables[variable_name]:
            self.variables[variable_name].append(procedure_name)

        # Registramos la variable dentro del procedimiento específico
        for proc_key in self.procedures:
            if proc_key[0] == procedure_name and variable_name not in self.procedures[proc_key]["variables"]:
                self.procedures[proc_key]["variables"].append(variable_name)

    def print_summary(self):
        print("Procedures and their variables:")
        for proc_key, data in self.procedures.items():
            print(f"{proc_key[0]} (params: {proc_key[1]}): {data['params']}, variables={data['variables']}")

        print("\nVariables and their procedures:")
        for var, procs in self.variables.items():
            print(f"{var}: {procs}")
