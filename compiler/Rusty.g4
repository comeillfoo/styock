grammar Rusty;
/*
 * Parser rules
 */
tuple_type : '(' ')' | '(' type (',' type)* ')';
type : UINT_TYPES | SINT_TYPES | FLOAT_TYPES | BOOL_TYPE | tuple_type ;

/* https://doc.rust-lang.org/reference/expressions/literal-expr.html */
literal_expression : INTEGER_LITERAL
    | 'true' | 'false';
negation_expression : '-' expression | '!' expression ;
arithmetic_or_logical_expression
    : expression '+' expression
    | expression '-' expression
    | expression '*' expression
    | expression '/' expression
    | expression '%' expression
    | expression '&' expression
    | expression '|' expression
    | expression '^' expression
    | expression '<<' expression
    | expression '>>' expression ;
comparison_expression
    : expression '==' expression
    | expression '!=' expression
    | expression '>' expression
    | expression '<' expression
    | expression '>=' expression
    | expression '<=' expression ;
lazy_boolean_expression
    : expression '||' expression
    | expression '&&' expression ;
/* https://doc.rust-lang.org/reference/expressions/operator-expr.html */
operator_expression : negation_expression | arithmetic_or_logical_expression
    | comparison_expression | lazy_boolean_expression ;
break_expression : 'break' ;
continue_expression : 'continue' ;
return_expression : 'return' expression? ;
expression_without_block : literal_expression | operator_expression
    | break_expression | continue_expression | return_expression ;

if_expression : 'if' expression block_expression ('else' (block_expression | if_expression))?;
iterator_loop_expression : 'for' 'mut'? IDENTIFIER 'in' expression block_expression ;
predicate_loop_expression : 'while' expression block_expression ;
infinite_loop_expression : 'loop' block_expression ;
loop_expression : infinite_loop_expression | predicate_loop_expression ;
expression_with_block : block_expression | loop_expression | if_expression ;
/* https://doc.rust-lang.org/reference/expressions.html */
expression : expression_with_block | expression_without_block ;

expression_statement : expression_with_block ';' | expression_without_block ';' ;
let_statement : 'let' 'mut'? IDENTIFIER (':' type)? ('=' expression)? ';' ;

statement : ';' | let_statement | expression_statement ;
block_expression : '{' statement* '}';

function_return_type : '->' type ;
function_param : IDENTIFIER ':' type ;
function_parameters : function_param (',' function_param)* ;
function : 'fn' IDENTIFIER '(' function_parameters? ')' function_return_type? (block_expression | ';');

/*
 * Lexer rules
 */
WHITESPACE : (' ' | '\t' | '\n' | '\r') -> skip;

fragment DEC_DIGIT : [0-9] ;
fragment HEX_DIGIT : DEC_DIGIT | [a-f] | [A-F] ;
fragment OCT_DIGIT : [0-7] ;
fragment BIN_DIGIT : [0-1] ;
fragment FLOAT_BIT_DEPTHS : '32' | '64' ;
fragment INTEGER_BIT_DEPTHS : '8' | '16' | FLOAT_BIT_DEPTHS | '128' ;
UINT_TYPES : 'u' INTEGER_BIT_DEPTHS ;
SINT_TYPES : 'i' INTEGER_BIT_DEPTHS ;
FLOAT_TYPES : 'f' FLOAT_BIT_DEPTHS ;
BOOL_TYPE : 'bool' ;

/* https://doc.rust-lang.org/reference/tokens.html#literals */
DEC_LITERAL : DEC_DIGIT (DEC_DIGIT| '_')* ;
HEX_LITERAL : '0x' (HEX_DIGIT | '_')* HEX_DIGIT (HEX_DIGIT | '_')* ;
OCT_LITERAL : '0o' (OCT_DIGIT | '_')* OCT_DIGIT (OCT_DIGIT | '_')* ;
BIN_LITERAL : '0b' (BIN_DIGIT | '_')* BIN_DIGIT (BIN_DIGIT | '_')*;
INTEGER_LITERAL : (BIN_LITERAL | OCT_LITERAL | DEC_LITERAL
    | HEX_LITERAL) (UINT_TYPES | SINT_TYPES)? ;

fragment FLOAT_EXPONENT : ('e' | 'E') ('+' | '-')? (DEC_DIGIT | '_')* DEC_DIGIT (DEC_DIGIT | '_')*;
FLOAT_LITERAL : DEC_LITERAL '.' | DEC_LITERAL '.' DEC_LITERAL
    | DEC_LITERAL ('.' DEC_LITERAL)? FLOAT_EXPONENT FLOAT_TYPES?;

/* https://doc.rust-lang.org/reference/identifiers.html */
fragment IDENTIFIER_START : [A-Z] | [a-z] | '_' ;
fragment IDENTIFIER_CONTINUE : IDENTIFIER_START | [0-9] ;
IDENTIFIER : IDENTIFIER_START IDENTIFIER_CONTINUE*;
