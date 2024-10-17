from ast_custom.node import ASTNode

class ProcedureStatement(ASTNode):
    def __init__(self, procedure_name, arguments, body):
        self.procedure_name = procedure_name
        self.arguments = arguments if arguments else []  # Lista de parámetros o vacío si no hay
        self.body = body if isinstance(body, list) else [body]  # Asegura que el cuerpo sea una lista

    def __repr__(self):
        return f"ProcedureStatement(name={self.procedure_name}, parameters={self.arguments}, body={self.body})"
