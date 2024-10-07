grammar Rusty;
/*
 * Parser rules
 */
types : UINT_TYPES | SINT_TYPES | FLOAT_TYPES | BOOL_TYPE | UNIT_TYPE ;

binary_op : '+' | '-' | '*' | '/' | '%' ;
unary_op : '-' ;
/* https://doc.rust-lang.org/reference/expressions/literal-expr.html */
literal_expression :
    | INTEGER_LITERAL
    | 'true' | 'false';

expression_without_block : literal_expression ;
expression_with_block : block_expression ;
expression : expression_with_block | expression_without_block ;

type_annotation : ':' types ;
variable_binding : 'let' 'mut'? IDENTIFIER type_annotation? '='
    (block_expression | expression) ;

statement : (variable_binding | expression) ';' ;
block_expression : '{' statement* '}';

function_argument : IDENTIFIER type_annotation ;
function_arguments : function_argument
    | function_argument ',' function_arguments ;
function : 'fn' IDENTIFIER '(' function_arguments? ')' ('->' types)? block_expression;

/*
 * Lexer rules
 */
WHITESPACE : (' ' | '\t' | '\n' | '\r') -> skip;

fragment NON_ZERO_DIGIT : [1-9] ;
fragment DIGIT : NON_ZERO_DIGIT | '0' ;
fragment HEX_DIGIT : DIGIT | [a-f] | [A-F] ;
fragment FLOAT_BIT_DEPTHS : '32' | '64' ;
fragment INTEGER_BIT_DEPTHS : '8' | '16' | FLOAT_BIT_DEPTHS | '128' ;
UINT_TYPES : 'u' INTEGER_BIT_DEPTHS ;
SINT_TYPES : 'i' INTEGER_BIT_DEPTHS ;
FLOAT_TYPES : 'f' FLOAT_BIT_DEPTHS ;
BOOL_TYPE : 'bool' ;
UNIT_TYPE : '()' ;

/* https://doc.rust-lang.org/reference/tokens.html#literals */
DECIMAL_LITERAL : NON_ZERO_DIGIT DIGIT* ;
HEXADECIMAL_LITERAL : '0x' HEX_DIGIT+ ;
OCTAL_LITERAL : '0o' [0-7]+ ;
BINARY_LITERAL : '0b' [0-1]+ ;
INTEGER_LITERAL : (BINARY_LITERAL | OCTAL_LITERAL | DECIMAL_LITERAL
    | HEXADECIMAL_LITERAL) (UINT_TYPES | SINT_TYPES)? ;

/* https://doc.rust-lang.org/reference/identifiers.html */
fragment IDENTIFIER_START : [A-Z] | [a-z] | '_' ;
fragment IDENTIFIER_CONTINUE : IDENTIFIER_START | [0-9] ;
IDENTIFIER : IDENTIFIER_START IDENTIFIER_CONTINUE*;
