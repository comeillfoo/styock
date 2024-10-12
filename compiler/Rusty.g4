grammar Rusty;
/*
 * Parser rules
 */
crate : item* ; /* aka starting rule */
item : function ;

tuple_type : '(' ')' | '(' type (',' type)* ')';
type
    : UINT_TYPES  # UnsignedIntegerType
    | SINT_TYPES  # SignedIntegerType
    | FLOAT_TYPES # FloatType
    | BOOL_TYPE   # BooleanType
    | tuple_type  # TupleType
    ;

negation_ops : ( '-' | '!' ) ;
arithmetic_or_logical_ops
    : ( '*' | '/' | '%' | '+' | '-' | '<<' | '>>' | '&' | '^' | '|' ) ;
comparison_ops : ( '==' | '!=' | '>' | '<' | '>=' | '<=' ) ;
lazy_boolean_ops : ( '&&' | '||' ) ;
binary_ops
    : arithmetic_or_logical_ops
    | comparison_ops
    | lazy_boolean_ops ;
call_params : expression (',' expression)* ;

if_expression : 'if' expression block_expression ('else' (block_expression | if_expression))?;

expression_with_block
    : block_expression
    | ('loop' | (('while' | 'for' 'mut'? IDENTIFIER 'in') expression)) block_expression
    | if_expression ;

/* https://doc.rust-lang.org/reference/expressions.html */
expression
/* https://doc.rust-lang.org/reference/expressions/literal-expr.html */
    : INTEGER_LITERAL | FLOAT_LITERAL | 'true' | 'false'
/* https://doc.rust-lang.org/reference/expressions/path-expr.html */
    | IDENTIFIER
/* https://doc.rust-lang.org/reference/expressions/call-expr.html */
    | expression '(' call_params? ')'
/* https://doc.rust-lang.org/reference/expressions/grouped-expr.html */
    | '(' expression ')'
/* https://doc.rust-lang.org/reference/expressions/operator-expr.html */
    | negation_ops expression
    | expression binary_ops expression
    | 'continue' | 'break' | 'return' expression?
    | expression_with_block ;


expression_statement
    : expression ';'
    | expression_with_block ';'? ;
let_statement : 'let' 'mut'? IDENTIFIER (':' type)? ('=' expression)? ';' ;

statement : ';' | let_statement | expression_statement ;
statements : statement+ | statement* expression ;
block_expression : '{' statements? '}';

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
UINT_TYPES : 'u' INTEGER_BIT_DEPTHS | 'usize' ;
SINT_TYPES : 'i' INTEGER_BIT_DEPTHS | 'isize' ;
FLOAT_TYPES : 'f' FLOAT_BIT_DEPTHS ;
BOOL_TYPE : 'bool' ;

/* https://doc.rust-lang.org/reference/tokens.html#literals */
fragment DEC_LITERAL : DEC_DIGIT (DEC_DIGIT| '_')* ;
fragment HEX_LITERAL : '0x' (HEX_DIGIT | '_')* HEX_DIGIT (HEX_DIGIT | '_')* ;
fragment OCT_LITERAL : '0o' (OCT_DIGIT | '_')* OCT_DIGIT (OCT_DIGIT | '_')* ;
fragment BIN_LITERAL : '0b' (BIN_DIGIT | '_')* BIN_DIGIT (BIN_DIGIT | '_')*;
INTEGER_LITERAL : (BIN_LITERAL | OCT_LITERAL | DEC_LITERAL
    | HEX_LITERAL) (UINT_TYPES | SINT_TYPES)? ;

fragment FLOAT_EXPONENT : ('e' | 'E') ('+' | '-')? (DEC_DIGIT | '_')* DEC_DIGIT (DEC_DIGIT | '_')*;
FLOAT_LITERAL : DEC_LITERAL '.' | DEC_LITERAL '.' DEC_LITERAL
    | DEC_LITERAL ('.' DEC_LITERAL)? FLOAT_EXPONENT FLOAT_TYPES?;

/* https://doc.rust-lang.org/reference/identifiers.html */
fragment IDENTIFIER_START : [A-Z] | [a-z] | '_' ;
fragment IDENTIFIER_CONTINUE : IDENTIFIER_START | [0-9] ;
IDENTIFIER : IDENTIFIER_START IDENTIFIER_CONTINUE*;
