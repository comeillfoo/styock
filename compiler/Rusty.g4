grammar Rusty;
/*
 * Parser rules
 */
crate : item* ; /* aka starting rule */
item : function ;

function : KW_FN IDENTIFIER LPAREN functionParams? RPAREN functionReturnType? blockExpression ;
functionParams : functionParam (COMMA functionParam)* ;
functionParam : KW_MUT? IDENTIFIER COLON type ;
functionReturnType : RARROW type ;

statement
    : SEMI                # StNopStatement
    | letStatement        # StLetStatement
    | expressionStatement # StExprStatement
    ;

letStatement : KW_LET KW_MUT? IDENTIFIER (COLON type)? (EQ expression)? SEMI ;

expressionStatement
    : expression SEMI
    | expressionWithBlock SEMI?
    ;

/* https://doc.rust-lang.org/reference/expressions.html */
expression
/* https://doc.rust-lang.org/reference/expressions/literal-expr.html */
    : INTEGER_LITERAL                                # IntegerLiteral
    | FLOAT_LITERAL                                  # FloatLiteral
    | KW_TRUE                                        # TrueLiteral
    | KW_FALSE                                       # FalseLiteral
/* https://doc.rust-lang.org/reference/expressions/path-expr.html */
    | IDENTIFIER                                     # PathExpr
/* https://doc.rust-lang.org/reference/expressions/call-expr.html */
    | IDENTIFIER LPAREN callParams? RPAREN           # CallExpr
/* https://doc.rust-lang.org/reference/expressions/operator-expr.html */
    | (MINUS | NOT) expression                       # NegationExpr
    | expression (STAR | SLASH | PERCENT) expression # ArithOrLogicExpr
    | expression (PLUS | MINUS) expression           # ArithOrLogicExpr
    | expression (SHL | SHR) expression              # ArithOrLogicExpr
    | expression AND expression                      # ArithOrLogicExpr
    | expression CARET expression                    # ArithOrLogicExpr
    | expression OR expression                       # ArithOrLogicExpr
    | expression comparisonOps expression            # ComparisonExpr
    | expression ANDAND expression                   # LazyBooleanExpr
    | expression OROR expression                     # LazyBooleanExpr
    | IDENTIFIER EQ expression                       # AssignmentExpr
    | IDENTIFIER compoundAssignOps expression        # CompoundAssignmentExpr
/* https://doc.rust-lang.org/reference/expressions/grouped-expr.html */
    | KW_CONTINUE                                    # ContinueExpr
    | KW_BREAK                                       # BreakExpr
    | KW_RETURN expression?                          # ReturnExpr
    | LPAREN expression RPAREN                       # GroupedExpr
    | expressionWithBlock                            # ExprWithBlock
    ;

comparisonOps
    : EQEQ
    | NEQ
    | GT
    | LT
    | GE
    | LE
    ;

compoundAssignOps
    : PLUSEQ
    | MINUSEQ
    | STAREQ
    | SLASHEQ
    | PERCENTEQ
    | ANDEQ
    | OREQ
    | CARETEQ
    | SHLEQ
    | SHREQ
    ;

expressionWithBlock
    : blockExpression                     # BlockExpr
    | KW_LOOP blockExpression             # infiniteLoopExpr
    | KW_WHILE expression blockExpression # predicateLoopExpr
    | ifExpression                        # IfExpr
    ;

statements : statement+ expression? | expression ;
blockExpression : LCURLYBR statements? RCURLYBR;

callParams : expression (COMMA expression)* ;

elseBranch : KW_ELSE ( blockExpression | ifExpression ) ;
ifExpression : KW_IF expression blockExpression elseBranch?;

tupleType : LPAREN RPAREN | LPAREN type (COMMA type)* RPAREN;
type
    : UINT_TYPES
    | SINT_TYPES
    | FLOAT_TYPES
    | BOOL_TYPE
    | tupleType
    ;
/*
 * Lexer rules
 */
KW_BREAK : 'break' ;
KW_CONTINUE : 'continue' ;
KW_ELSE : 'else' ;
KW_FALSE : 'false' ;
KW_FN : 'fn' ;
KW_IF : 'if' ;
KW_LET : 'let' ;
KW_LOOP : 'loop' ;
KW_MUT : 'mut' ;
KW_RETURN : 'return' ;
KW_TRUE : 'true' ;
KW_WHILE : 'while' ;

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

PLUS : '+' ;
MINUS : '-' ;
STAR : '*' ;
SLASH : '/' ;
PERCENT : '%' ;
CARET : '^' ;
NOT : '!' ;
AND : '&' ;
OR : '|' ;
ANDAND : '&&' ;
OROR : '||' ;
SHL : '<<' ;
SHR : '>>' ;

PLUSEQ : '+=' ;
MINUSEQ : '-=' ;
STAREQ : '*=' ;
SLASHEQ : '/=' ;
PERCENTEQ : '%=' ;
CARETEQ : '^=' ;
ANDEQ : '&=' ;
OREQ : '|=' ;
SHLEQ : '<<=' ;
SHREQ : '>>=' ;
EQ : '=' ;

EQEQ : '==' ;
NEQ : '!=' ;
GT : '>' ;
LT : '<' ;
GE : '>=' ;
LE : '<=' ;
COMMA : ',' ;
SEMI : ';' ;
COLON : ':' ;
RARROW : '->' ;

LCURLYBR : '{' ;
RCURLYBR : '}' ;
LPAREN : '(' ;
RPAREN : ')' ;
