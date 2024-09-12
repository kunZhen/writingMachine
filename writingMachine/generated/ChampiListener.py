# Generated from Champi.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ChampiParser import ChampiParser
else:
    from ChampiParser import ChampiParser

# This class defines a complete listener for a parse tree produced by ChampiParser.
class ChampiListener(ParseTreeListener):

    # Enter a parse tree produced by ChampiParser#program.
    def enterProgram(self, ctx:ChampiParser.ProgramContext):
        pass

    # Exit a parse tree produced by ChampiParser#program.
    def exitProgram(self, ctx:ChampiParser.ProgramContext):
        pass


    # Enter a parse tree produced by ChampiParser#VarAssignStatement.
    def enterVarAssignStatement(self, ctx:ChampiParser.VarAssignStatementContext):
        pass

    # Exit a parse tree produced by ChampiParser#VarAssignStatement.
    def exitVarAssignStatement(self, ctx:ChampiParser.VarAssignStatementContext):
        pass


    # Enter a parse tree produced by ChampiParser#PrintlnStatement.
    def enterPrintlnStatement(self, ctx:ChampiParser.PrintlnStatementContext):
        pass

    # Exit a parse tree produced by ChampiParser#PrintlnStatement.
    def exitPrintlnStatement(self, ctx:ChampiParser.PrintlnStatementContext):
        pass


    # Enter a parse tree produced by ChampiParser#varAssign.
    def enterVarAssign(self, ctx:ChampiParser.VarAssignContext):
        pass

    # Exit a parse tree produced by ChampiParser#varAssign.
    def exitVarAssign(self, ctx:ChampiParser.VarAssignContext):
        pass


    # Enter a parse tree produced by ChampiParser#println.
    def enterPrintln(self, ctx:ChampiParser.PrintlnContext):
        pass

    # Exit a parse tree produced by ChampiParser#println.
    def exitPrintln(self, ctx:ChampiParser.PrintlnContext):
        pass


    # Enter a parse tree produced by ChampiParser#NumberExpr.
    def enterNumberExpr(self, ctx:ChampiParser.NumberExprContext):
        pass

    # Exit a parse tree produced by ChampiParser#NumberExpr.
    def exitNumberExpr(self, ctx:ChampiParser.NumberExprContext):
        pass


    # Enter a parse tree produced by ChampiParser#VarRefExpr.
    def enterVarRefExpr(self, ctx:ChampiParser.VarRefExprContext):
        pass

    # Exit a parse tree produced by ChampiParser#VarRefExpr.
    def exitVarRefExpr(self, ctx:ChampiParser.VarRefExprContext):
        pass



del ChampiParser