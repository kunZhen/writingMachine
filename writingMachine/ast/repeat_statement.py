from writingMachine.ast.node import ASTNode


class RepeatStatement(ASTNode):
    def __init__(self, body, condition):
        self.body = body if isinstance(body, list) else [body]
        self.condition = condition

    def __repr__(self):
        return f"RepeatStatement(body={self.body}, condition={self.condition})"