from ast_custom.node import ASTNode

class ForStatement(ASTNode):
    def __init__(self, variable, min_value, max_value, body):
        self.variable = variable
        self.min_value = min_value
        self.max_value = max_value
        self.body = body if isinstance(body, list) else [body]

    def __repr__(self):
        return f"ForStatement(variable={self.variable}, min_value={self.min_value}, max_value={self.max_value}, body={self.body})"
