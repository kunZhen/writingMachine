from ast_custom.node import ASTNode

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body if isinstance(body, list) else [body]

    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={self.body})"