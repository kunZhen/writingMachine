from typing import Dict

class ASTNode:
    def execute(self, symbolTable: Dict[str, object]):
        raise NotImplementedError("Must be implemented in subclass")
