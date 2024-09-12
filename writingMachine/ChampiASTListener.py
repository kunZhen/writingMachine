from generated.ChampiListener import ChampiListener
from generated.ChampiParser import ChampiParser
from ast import Constant, Println, VarAssign, VarRef

class ChampiASTListener(ChampiListener):
    def __init__(self):
        self.symbolTable = {}

    def enterVarAssignStatement(self, ctx: ChampiParser.VarAssignStatementContext):
        var_assign_ctx = ctx.varAssign()  # Obtiene el contexto varAssign del contexto VarAssignStatementContext
        name = var_assign_ctx.IDENTIFIER().getText()  # Obtiene el identificador de la variable
        expr = self.visitExpr(var_assign_ctx.expr())  # Visita la expresión
        var_assign = VarAssign(name, expr)  # Crea una instancia de VarAssign
        var_assign.execute(self.symbolTable)  # Ejecuta la asignación

    def enterPrintlnStatement(self, ctx: ChampiParser.PrintlnStatementContext):
        println_ctx = ctx.println()  # Obtiene el contexto println del contexto PrintlnStatementContext
        expr = self.visitExpr(println_ctx.expr())  # Visita la expresión
        println = Println(expr)  # Crea una instancia de Println
        println.execute(self.symbolTable)  # Ejecuta el println

    def visitNumberExpr(self, ctx: ChampiParser.NumberExprContext):
        return Constant(int(ctx.NUMBER().getText()))  # Crea un Constant con el valor del número

    def visitVarRefExpr(self, ctx: ChampiParser.VarRefExprContext):
        return VarRef(ctx.IDENTIFIER().getText())  # Crea un VarRef con el nombre de la variable

    def visitExpr(self, ctx):
        # Determina el tipo de expresión y llama al método adecuado
        if isinstance(ctx, ChampiParser.NumberExprContext):
            return self.visitNumberExpr(ctx)  # Llama a visitNumberExpr si el contexto es un número
        elif isinstance(ctx, ChampiParser.VarRefExprContext):
            return self.visitVarRefExpr(ctx)  # Llama a visitVarRefExpr si el contexto es una variable
        else:
            raise Exception(f"Unexpected expression context: {ctx}")  # Lanza excepción si el contexto no es esperado