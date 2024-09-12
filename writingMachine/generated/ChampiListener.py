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


    # Enter a parse tree produced by ChampiParser#statement.
    def enterStatement(self, ctx:ChampiParser.StatementContext):
        pass

    # Exit a parse tree produced by ChampiParser#statement.
    def exitStatement(self, ctx:ChampiParser.StatementContext):
        pass



del ChampiParser