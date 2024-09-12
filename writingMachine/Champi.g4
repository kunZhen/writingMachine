grammar Champi;

program: statement+ ;
statement: 'println' '(' STRING ')' ';' ;

STRING: '"' (ESC | ~["\\])* '"' ;
fragment ESC: '\\' ["/bfnrt] ;
WS: [ \t\r\n]+ -> skip ;
