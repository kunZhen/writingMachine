from writingMachine.ast.node import ASTNode

class ProcedureStatement(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params if isinstance(params, list) else [params]  # Aseguramos que los parámetros sean una lista
        self.body = body if isinstance(body, list) else [body]  # Aseguramos que el cuerpo también sea una lista

    def __repr__(self):
        return f"ProcedureStatement(name={self.name}, params={self.params}, body={self.body})"
