grammar Champi;

program : (statement)* EOF;

statement
    : varAssign            # VarAssignStatement
    | println              # PrintlnStatement
    ;

varAssign : IDENTIFIER '=' expr ';';
println   : 'println' '(' expr ')' ';';

expr
    : NUMBER               # NumberExpr
    | IDENTIFIER           # VarRefExpr
    ;

IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9]*;
NUMBER     : [0-9]+;
WS         : [ \t\r\n]+ -> skip;
