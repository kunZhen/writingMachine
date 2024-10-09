class ASTNode:
    """Clase base para todos los nodos del AST."""
    def accept(self, visitor):
        """Cada nodo del AST deberá implementar este método para ser visitado."""
        raise NotImplementedError("El método 'accept' debe ser implementado en las subclases")

class Statement(ASTNode):
    """Clase base para todos los nodos de statement."""
    pass

class Expression(ASTNode):
    """Clase base para todos los nodos de expresión."""
    pass
