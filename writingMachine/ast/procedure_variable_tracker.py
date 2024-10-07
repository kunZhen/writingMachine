class ProcedureVariableTracker:
    def __init__(self):
        self.procedures = {}  # {procedure_name: {params: [], variables: []}}
        self.variables = {}  # {variable_name: [procedure_names]}

    def register_procedure(self, procedure_name, parameters):
        if procedure_name not in self.procedures:
            self.procedures[procedure_name] = {"params": parameters, "variables": []}
        for param in parameters:
            self.register_variable(param, procedure_name)

    def register_variable(self, variable_name, procedure_name):
        if variable_name not in self.variables:
            self.variables[variable_name] = []
        if procedure_name not in self.variables[variable_name]:
            self.variables[variable_name].append(procedure_name)

        if procedure_name in self.procedures:
            if variable_name not in self.procedures[procedure_name]["variables"]:
                self.procedures[procedure_name]["variables"].append(variable_name)

    def get_procedures_for_variable(self, variable_name):
        return self.variables.get(variable_name, [])

    def get_variables_for_procedure(self, procedure_name):
        return self.procedures.get(procedure_name, {"variables": []})["variables"]

    def print_summary(self):
        print("Procedures and their variables:")
        for proc, data in self.procedures.items():
            print(f"{proc}: parameters={data['params']}, variables={data['variables']}")
        print("\nVariables and their procedures:")
        for var, procs in self.variables.items():
            print(f"{var}: {procs}")