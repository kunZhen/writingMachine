# Generated from Champi.g4 by ANTLR 4.9.3
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\n")
        buf.write("(\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\7\2\16\n")
        buf.write("\2\f\2\16\2\21\13\2\3\2\3\2\3\3\3\3\5\3\27\n\3\3\4\3\4")
        buf.write("\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\5\6&\n\6")
        buf.write("\3\6\2\2\7\2\4\6\b\n\2\2\2%\2\17\3\2\2\2\4\26\3\2\2\2")
        buf.write("\6\30\3\2\2\2\b\35\3\2\2\2\n%\3\2\2\2\f\16\5\4\3\2\r\f")
        buf.write("\3\2\2\2\16\21\3\2\2\2\17\r\3\2\2\2\17\20\3\2\2\2\20\22")
        buf.write("\3\2\2\2\21\17\3\2\2\2\22\23\7\2\2\3\23\3\3\2\2\2\24\27")
        buf.write("\5\6\4\2\25\27\5\b\5\2\26\24\3\2\2\2\26\25\3\2\2\2\27")
        buf.write("\5\3\2\2\2\30\31\7\b\2\2\31\32\7\3\2\2\32\33\5\n\6\2\33")
        buf.write("\34\7\4\2\2\34\7\3\2\2\2\35\36\7\5\2\2\36\37\7\6\2\2\37")
        buf.write(" \5\n\6\2 !\7\7\2\2!\"\7\4\2\2\"\t\3\2\2\2#&\7\t\2\2$")
        buf.write("&\7\b\2\2%#\3\2\2\2%$\3\2\2\2&\13\3\2\2\2\5\17\26%")
        return buf.getvalue()


class ChampiParser ( Parser ):

    grammarFileName = "Champi.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'='", "';'", "'println'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "IDENTIFIER", "NUMBER", 
                      "WS" ]

    RULE_program = 0
    RULE_statement = 1
    RULE_varAssign = 2
    RULE_println = 3
    RULE_expr = 4

    ruleNames =  [ "program", "statement", "varAssign", "println", "expr" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    IDENTIFIER=6
    NUMBER=7
    WS=8

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.3")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(ChampiParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChampiParser.StatementContext)
            else:
                return self.getTypedRuleContext(ChampiParser.StatementContext,i)


        def getRuleIndex(self):
            return ChampiParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = ChampiParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==ChampiParser.T__2 or _la==ChampiParser.IDENTIFIER:
                self.state = 10
                self.statement()
                self.state = 15
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 16
            self.match(ChampiParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ChampiParser.RULE_statement

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class PrintlnStatementContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ChampiParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def println(self):
            return self.getTypedRuleContext(ChampiParser.PrintlnContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintlnStatement" ):
                listener.enterPrintlnStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintlnStatement" ):
                listener.exitPrintlnStatement(self)


    class VarAssignStatementContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ChampiParser.StatementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def varAssign(self):
            return self.getTypedRuleContext(ChampiParser.VarAssignContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarAssignStatement" ):
                listener.enterVarAssignStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarAssignStatement" ):
                listener.exitVarAssignStatement(self)



    def statement(self):

        localctx = ChampiParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 20
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ChampiParser.IDENTIFIER]:
                localctx = ChampiParser.VarAssignStatementContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self.varAssign()
                pass
            elif token in [ChampiParser.T__2]:
                localctx = ChampiParser.PrintlnStatementContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 19
                self.println()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VarAssignContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(ChampiParser.IDENTIFIER, 0)

        def expr(self):
            return self.getTypedRuleContext(ChampiParser.ExprContext,0)


        def getRuleIndex(self):
            return ChampiParser.RULE_varAssign

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarAssign" ):
                listener.enterVarAssign(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarAssign" ):
                listener.exitVarAssign(self)




    def varAssign(self):

        localctx = ChampiParser.VarAssignContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_varAssign)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(ChampiParser.IDENTIFIER)
            self.state = 23
            self.match(ChampiParser.T__0)
            self.state = 24
            self.expr()
            self.state = 25
            self.match(ChampiParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrintlnContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(ChampiParser.ExprContext,0)


        def getRuleIndex(self):
            return ChampiParser.RULE_println

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintln" ):
                listener.enterPrintln(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintln" ):
                listener.exitPrintln(self)




    def println(self):

        localctx = ChampiParser.PrintlnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_println)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.match(ChampiParser.T__2)
            self.state = 28
            self.match(ChampiParser.T__3)
            self.state = 29
            self.expr()
            self.state = 30
            self.match(ChampiParser.T__4)
            self.state = 31
            self.match(ChampiParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ChampiParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class NumberExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ChampiParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(ChampiParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumberExpr" ):
                listener.enterNumberExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumberExpr" ):
                listener.exitNumberExpr(self)


    class VarRefExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ChampiParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER(self):
            return self.getToken(ChampiParser.IDENTIFIER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarRefExpr" ):
                listener.enterVarRefExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarRefExpr" ):
                listener.exitVarRefExpr(self)



    def expr(self):

        localctx = ChampiParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_expr)
        try:
            self.state = 35
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ChampiParser.NUMBER]:
                localctx = ChampiParser.NumberExprContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 33
                self.match(ChampiParser.NUMBER)
                pass
            elif token in [ChampiParser.IDENTIFIER]:
                localctx = ChampiParser.VarRefExprContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 34
                self.match(ChampiParser.IDENTIFIER)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





