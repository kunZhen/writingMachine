from writingMachine.ast.node import ASTNode

class ProcedureStatement(ASTNode):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters if parameters else []  # Lista de parámetros o vacío si no hay
        self.body = body if isinstance(body, list) else [body]  # Asegura que el cuerpo sea una lista

    def __repr__(self):
        return f"ProcedureStatement(name={self.name}, parameters={self.parameters}, body={self.body})"
