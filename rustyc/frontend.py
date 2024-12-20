#!/usr/bin/env python3
'''Модуль, реализующий трансляцию подмножества языка Rust в инструкции стековой
виртуальной машины. На данном (первом) этапе трансляции все метки в программе
остаются нетронутыми - т.е. в виде текста.

Реализация трансляции взята напрямую из документации ANTLR4, в которой класс
Listener поддерживает словарь (map) между *контекстом* распарсенной конструкции
языка и строкой с результирующими инструкциями. Т.е. класс обработчик кэширует
соответствия между входным набором токеном и результатом их трансляции.

Так как *контекст* представляет собой объект, хэш которого это уникальный
идентификатор данного объекта в памяти, то коллизии в данном словаре исключены.
'''
from typing import Optional
from dataclasses import dataclass

from .libs.RustyListener import RustyListener
from .libs.RustyParser import RustyParser


@dataclass
class VariableMeta:
    '''Stores metadata for a single variable. Metadata consists of variable's
    numerical identifier and sign of its mutability. Numerical identifiers are
    used for `store` and `load` VM instructions.
    '''
    identifier: int = 0
    mutable: bool = False

@dataclass
class FnMeta:
    '''Stores metadata for a single function. Metadata consists of function's
    name, its parameters and local variables. Parameters and local variables are
    represented with maps (dictionaries) that keeps matching between variable's
    name and variable's metadata (numerical identifier).

    Parameters and local variables are enumerated end-to-end. Thus, numerical
    identifier of every local variable is strictly greater than every identifier
    of every function parameter.
    '''
    name: str
    parameters: dict[str, VariableMeta]
    locals: dict[str, VariableMeta]


def finstr(ins: str) -> str:
    '''Formats program's instruction by prepending tab to distinguish them from
    labels.

    :param ins: single VM instruction
    :type ins: str

    :return: line with tab and instruction
    :rtype: str
    '''
    return '\t' + ins


def flabel(lbl: str) -> str:
    '''Formats program's label to distinguish them from the instructions.

    :param lbl: program's label
    :type lbl: str

    :return: line with label name and colon (:) at the end
    :rtype: str
    '''
    return lbl + ':'


class FERListener(RustyListener):
    '''Handlers for parse rules. An observer in the oberver pattern. Builds a map
    of translations from input subset of Rust to VM instructions.

    At the beginning of every module (crate) puts `call main` and `stop`:
    ```
    0: call main
    1: stop
    2: ...
    ```
    '''
    def __init__(self):
        super().__init__()
        self.tree = {}
        self.functions: dict[str, FnMeta] = {}
        self.counter = 0
        self.current_function: Optional[str] = None
        self.loop_labels = []

    def next_label(self, name: str) -> str:
        '''Generates unique label with specified name. Every call increments
        internal labels counter.

        :param name: meaningful name of the label
        :type name: str

        :return: label
        :rtype: str
        '''
        salt = f'.{self.counter}_'
        pepper = '_utlbl'
        self.counter += 1
        return salt + name + pepper

# Implement NegationExprs alternatives
    def exitNegationExpr(self, ctx: RustyParser.NegationExprContext):
        instruction = {
            (True, False): 'neg',
            (False, True): 'not'
        }.get((ctx.MINUS() is not None, ctx.NOT() is not None))
        self.tree[ctx] = '\n'.join([
            self.tree[ctx.expression()],
            finstr(instruction)
        ])
        return super().exitNegationExpr(ctx)

# Implement ArithOrLogicExprs alternatives
    def exitArithOrLogicExpr(self, ctx: RustyParser.ArithOrLogicExprContext):
        instruction = 'nop'
        if ctx.STAR() is not None:
            instruction = 'mul'
        elif ctx.SLASH() is not None:
            instruction = 'div'
        elif ctx.PERCENT() is not None:
            instruction = 'mod'
        elif ctx.PLUS() is not None:
            instruction = 'add'
        elif ctx.MINUS() is not None:
            instruction = 'sub'
        elif ctx.SHL() is not None:
            instruction = 'shl'
        elif ctx.SHR() is not None:
            instruction = 'shr'
        elif ctx.AND() is not None:
            instruction = 'and'
        elif ctx.CARET() is not None:
            instruction = 'xor'
        elif ctx.OR() is not None:
            instruction = 'or'
        else:
            raise Exception # Unsupported operator
        self.tree[ctx] = '\n'.join([
            self.tree[ctx.expression()[0]],
            self.tree[ctx.expression()[1]],
            finstr(instruction)
        ])
        return super().exitArithOrLogicExpr(ctx)

# Implement ComparisonOps alternatives
    def exitComparisonOps(self, ctx: RustyParser.ComparisonOpsContext):
        instruction = 'nop'
        if ctx.EQEQ() is not None:
            instruction = 'eq'
        elif ctx.NEQ() is not None:
            instruction = 'neq'
        elif ctx.GT() is not None:
            instruction = 'gt'
        elif ctx.LT() is not None:
            instruction = 'lt'
        elif ctx.GE() is not None:
            instruction = 'ge'
        elif ctx.LE() is not None:
            instruction = 'le'
        else:
            raise Exception # unsupported comparison operator
        self.tree[ctx] = finstr(instruction)
        return super().exitComparisonOps(ctx)

# Implement CompoundAssignmentOps alternatives
    def exitCompoundAssignOps(self, ctx: RustyParser.CompoundAssignOpsContext):
        instruction = 'nop'
        if ctx.PLUSEQ() is not None:
            instruction = 'add'
        elif ctx.MINUSEQ() is not None:
            instruction = 'sub'
        elif ctx.STAREQ() is not None:
            instruction = 'mul'
        elif ctx.SLASHEQ() is not None:
            instruction = 'div'
        elif ctx.PERCENTEQ() is not None:
            instruction = 'mod'
        elif ctx.ANDEQ() is not None:
            instruction = 'and'
        elif ctx.OREQ() is not None:
            instruction = 'or'
        elif ctx.CARETEQ() is not None:
            instruction = 'xor'
        elif ctx.SHLEQ() is not None:
            instruction = 'shl'
        elif ctx.SHREQ() is not None:
            instruction = 'shr'
        else:
            raise Exception # unsupported compound operator
        self.tree[ctx] = finstr(instruction)
        return super().exitCompoundAssignOps(ctx)

# Implement LazyBooleanExprs alternatives
    def exitLazyBooleanExpr(self, ctx: RustyParser.LazyBooleanExprContext):
        instruction = {
            (True, False): 'and',
            (False, True): 'or'
        }.get((ctx.ANDAND() is not None, ctx.OROR() is not None))
        self.tree[ctx] = '\n'.join([
            self.tree[ctx.expression()[0]],
            self.tree[ctx.expression()[1]],
            finstr(instruction)
        ])
        return super().exitLazyBooleanExpr(ctx)

# Implement callParams
    def exitCallParams(self, ctx: RustyParser.CallParamsContext):
        self.tree[ctx] = '\n'.join(map(self.tree.get, ctx.expression()))
        return super().exitCallParams(ctx)

# Implement ifExpression rule
    def exitElseBranch(self, ctx: RustyParser.ElseBranchContext):
        if ctx.blockExpression() is not None:
            self.tree[ctx] = self.tree[ctx.blockExpression()]
        elif ctx.ifExpression is not None:
            self.tree[ctx] = self.tree[ctx.ifExpression()]
        else:
            raise Exception # malformed parsing rules
        return super().exitElseBranch(ctx)

    def exitIfExpression(self, ctx: RustyParser.IfExpressionContext):
        lbl_fi = self.next_label('fi')
        lbl_then = self.next_label('then')

        instructions = [
            self.tree[ctx.expression()],
            finstr('jift ' + lbl_then)
        ]
        if ctx.elseBranch() is not None:
            instructions.append(self.tree[ctx.elseBranch()])
        instructions.extend([
            finstr('jmp ' + lbl_fi),
            flabel(lbl_then),
            self.tree[ctx.blockExpression()],
            flabel(lbl_fi)
        ])

        self.tree[ctx] = '\n'.join(instructions)
        return super().exitIfExpression(ctx)

# Implement blockExpression
    def exitBlockExpression(self, ctx: RustyParser.BlockExpressionContext):
        statements = ctx.statements()
        self.tree[ctx] = '' if statements is None else self.tree[statements]
        return super().exitBlockExpression(ctx)

# Implement statements
    def exitStatements(self, ctx: RustyParser.StatementsContext):
        instructions = []
        if ctx.statement() is not None:
            instructions.extend(map(self.tree.get, ctx.statement()))
        if ctx.expression() is not None:
            instructions.append(self.tree[ctx.expression()])
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitStatements(ctx)

# Implement expressionWithBlock alternatives
    def exitBlockExpr(self, ctx: RustyParser.BlockExprContext):
        self.tree[ctx] = self.tree[ctx.blockExpression()]
        return super().exitBlockExpr(ctx)

    def enterInfiniteLoopExpr(self, ctx: RustyParser.InfiniteLoopExprContext):
        self.loop_labels.append((
            self.next_label('info_enter'),
            self.next_label('inflo_exit')
        ))
        return super().enterInfiniteLoopExpr(ctx)

    def exitInfiniteLoopExpr(self, ctx: RustyParser.InfiniteLoopExprContext):
        lbl_loop_enter, lbl_loop_exit = self.loop_labels.pop()
        self.tree[ctx] = '\n'.join([
            flabel(lbl_loop_enter),
            self.tree[ctx.blockExpression()],
            finstr('jmp ' + lbl_loop_enter),
            flabel(lbl_loop_exit)
        ])
        return super().exitInfiniteLoopExpr(ctx)

    def enterPredicateLoopExpr(self, ctx: RustyParser.PredicateLoopExprContext):
        self.loop_labels.append((
            self.next_label('predlo_cond'),
            self.next_label('predlo_exit')
        ))
        return super().enterPredicateLoopExpr(ctx)

    def exitPredicateLoopExpr(self, ctx: RustyParser.PredicateLoopExprContext):
        lbl_loop_cond, lbl_loop_exit = self.loop_labels.pop()
        lbl_loop_enter = self.next_label('predlo_enter')

        self.tree[ctx] = '\n'.join([
            finstr('jmp ' + lbl_loop_cond),
            flabel(lbl_loop_enter),
            self.tree[ctx.blockExpression()],
            flabel(lbl_loop_cond),
            self.tree[ctx.expression()],
            finstr('jift ' + lbl_loop_enter),
            flabel(lbl_loop_exit)
        ])
        return super().exitPredicateLoopExpr(ctx)

    def exitIfExpr(self, ctx: RustyParser.IfExprContext):
        self.tree[ctx] = self.tree[ctx.ifExpression()]
        return super().exitIfExpr(ctx)

# Implement expression alternatives
    def exitIntegerLiteral(self, ctx: RustyParser.IntegerLiteralContext):
        integer_literal = str(ctx.INTEGER_LITERAL())
        for signedness in ('u', 'i'):
            for bit_depth in ('8', '16', '32', '64', '128', 'size'):
                integer_literal = integer_literal.replace(signedness + bit_depth,
                                                          '')
        self.tree[ctx] = finstr('push ' + integer_literal)
        return super().exitIntegerLiteral(ctx)

    def exitFloatLiteral(self, ctx: RustyParser.FloatLiteralContext):
        self.tree[ctx] = finstr('push ' + str(ctx.FLOAT_LITERAL()))
        return super().exitFloatLiteral(ctx)

    def exitTrueLiteral(self, ctx: RustyParser.TrueLiteralContext):
        self.tree[ctx] = finstr('push 1')
        return super().exitTrueLiteral(ctx)

    def exitFalseLiteral(self, ctx: RustyParser.FalseLiteralContext):
        self.tree[ctx] = finstr('push 0')
        return super().exitFalseLiteral(ctx)

    def _get_variable(self, variable_name: str) -> VariableMeta:
        '''Returns variable's metadata by its name.

        :param self: instance of listener
        :type self: class:`rustyc.frontend.FERListener`
        :param variable_name: variable's name
        :type variable_name: str

        :return: variable's metadata
        :rtype: class:`rustyc.frontend.VariableMeta`
        '''
        parameters = self.functions[self.current_function].parameters
        try:
            return parameters[variable_name]
        except KeyError:
            pass
        try:
            return self.functions[self.current_function].locals[variable_name]
        except KeyError:
            raise Exception # variable is not defined

    def exitPathExpr(self, ctx: RustyParser.PathExprContext):
        variable = self._get_variable(str(ctx.IDENTIFIER()))
        self.tree[ctx] = finstr(f'load {variable.identifier}')
        return super().exitPathExpr(ctx)

    def exitCallExpr(self, ctx: RustyParser.CallExprContext):
        instructions = []
        if ctx.callParams() is not None:
            instructions.append(self.tree[ctx.callParams()])
        instructions.append(finstr('call ' + str(ctx.IDENTIFIER())))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitCallExpr(ctx)

    def exitComparisonExpr(self, ctx: RustyParser.ComparisonExprContext):
        self.tree[ctx] = '\n'.join([
            self.tree[ctx.expression()[0]],
            self.tree[ctx.expression()[1]],
            self.tree[ctx.comparisonOps()]
        ])
        return super().exitComparisonExpr(ctx)

    def exitAssignmentExpr(self, ctx: RustyParser.AssignmentExprContext):
        variable = self._get_variable(str(ctx.IDENTIFIER()))
        if not variable.mutable:
            raise Exception # variable is immutable
        instructions = [self.tree[ctx.expression()]]
        instructions.append(finstr(f'store {variable.identifier}'))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitAssignmentExpr(ctx)

    def exitCompoundAssignmentExpr(self, ctx: RustyParser.CompoundAssignmentExprContext):
        variable = self._get_variable(str(ctx.IDENTIFIER()))
        if not variable.mutable:
            raise Exception # variable is immutable

        self.tree[ctx] = '\n'.join([
            finstr(f'load {variable.identifier}'),
            self.tree[ctx.expression()],
            self.tree[ctx.compoundAssignOps()],
            finstr(f'store {variable.identifier}')
        ])
        return super().exitCompoundAssignmentExpr(ctx)

    def exitContinueExpr(self, ctx: RustyParser.ContinueExprContext):
        continue_label, _ = self.loop_labels[-1]
        self.tree[ctx] = finstr('jmp ' + continue_label)
        return super().exitContinueExpr(ctx)

    def exitBreakExpr(self, ctx: RustyParser.BreakExprContext):
        _, break_label = self.loop_labels[-1]
        self.tree[ctx] = finstr('jmp ' + break_label)
        return super().exitBreakExpr(ctx)

    def exitReturnExpr(self, ctx: RustyParser.ReturnExprContext):
        instructions = []
        if ctx.expression() is not None:
            instructions.append(self.tree[ctx.expression()])
        instructions.append(finstr('ret'))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitReturnExpr(ctx)

    def exitGroupedExpr(self, ctx: RustyParser.GroupedExprContext):
        self.tree[ctx] = self.tree[ctx.expression()]
        return super().exitGroupedExpr(ctx)

    def exitExprWithBlock(self, ctx: RustyParser.ExprWithBlockContext):
        self.tree[ctx] = self.tree[ctx.getChild()]
        return super().exitExprWithBlock(ctx)

# Implement expressionStatement
    def exitExpressionStatement(self, ctx: RustyParser.ExpressionStatementContext):
        if ctx.expression() is not None:
            self.tree[ctx] = self.tree[ctx.expression()]
        elif ctx.expressionWithBlock() is not None:
            self.tree[ctx] = self.tree[ctx.expressionWithBlock()]
        else:
            raise Exception # malformed parsing rules
        return super().exitExpressionStatement(ctx)

# Implement letStatement
    def exitLetStatement(self, ctx: RustyParser.LetStatementContext):
        def _add_local_variable(variable_name: str,
                                is_mutable: bool = False) -> VariableMeta:
            '''Builds local variable's metadata and adds it to the current
            function. As functions are the only top-level things and functions
            cannot be declared inside functions they could be traced with single
            variable current_function.

            :param variable_name: local variable name
            :type variable_name: str
            :param is_mutable: is it allowed to change variable value
            :type is_mutable: bool, default False

            :return: created variable's metadata
            :rtype: class:`rustyc.frontend.VariableMeta`
            '''
            current_function = self.functions[self.current_function]
            if variable_name in current_function.parameters:
                raise Exception # variable already defined as parameter
            if variable_name in current_function.locals:
                raise Exception # variable already defined as local variable
            last_id = len(current_function.parameters) + len(current_function.locals)
            self.functions[self.current_function] \
                .locals[variable_name] = VariableMeta(last_id, is_mutable)
            return self.functions[self.current_function].locals[variable_name]

        variable = _add_local_variable(str(ctx.IDENTIFIER()),
                                       ctx.KW_MUT() is not None)
        instructions = []
        if ctx.expression() is not None:
            instructions.append(self.tree[ctx.expression()])
        else:
            # init with the default value
            instructions.append(finstr('push 0'))
        instructions.append(finstr(f'store {variable.identifier}'))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitLetStatement(ctx)

# Implement statement alternatives
    def exitStNopStatement(self, ctx: RustyParser.StNopStatementContext):
        self.tree[ctx] = finstr('nop')
        return super().exitStNopStatement(ctx)

    def exitStLetStatement(self, ctx: RustyParser.StLetStatementContext):
        self.tree[ctx] = self.tree[ctx.letStatement()]
        return super().exitStLetStatement(ctx)

    def exitStExprStatement(self, ctx: RustyParser.StExprStatementContext):
        self.tree[ctx] = self.tree[ctx.expressionStatement()]
        return super().exitStExprStatement(ctx)

# Implement function rule
    def enterFunction(self, ctx: RustyParser.FunctionContext):
        def _list_parameters(ctx: RustyParser.FunctionContext) -> dict[str, VariableMeta]:
            '''Builds map of parameter name to its metadata as a variable

            :param ctx: context for function rule
            :type ctx: class:`RustyParser.FunctionContext`

            :return: map of function's parameters
            :rtype: dict[str, class:`rustyc.frontend.VariableMeta`]
            '''
            if ctx.functionParams() is None:
                return {}

            parameters = {}
            for i, param_ctx in enumerate(ctx.functionParams().functionParam()):
                param_name = str(param_ctx.IDENTIFIER())
                if param_name in parameters:
                    raise Exception # parameter already used
                parameters[param_name] = VariableMeta(i,
                    param_ctx.KW_MUT() is not None)
            return parameters

        self.current_function = str(ctx.IDENTIFIER())
        if self.current_function in self.functions:
            raise Exception # function already defined
        self.functions[self.current_function] = FnMeta(self.current_function,
            _list_parameters(ctx), {})
        return super().enterFunction(ctx)

    def exitFunction(self, ctx: RustyParser.FunctionContext):
        instructions = [str(ctx.IDENTIFIER()) + ':']
        save_instructions = map(lambda id: finstr(f'store {id}'),
            reversed(sorted(list(map(lambda var: var.identifier,
                                     self.functions[self.current_function].parameters.values())))))
        instructions.extend(save_instructions)
        instructions.extend([
            self.tree[ctx.blockExpression()],
            finstr('ret')
        ])
        self.current_function = None
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitFunction(ctx)

# Implement root rules (crate and item)
    def exitItem(self, ctx: RustyParser.ItemContext):
        self.tree[ctx] = self.tree[ctx.function()]
        return super().exitItem(ctx)

    def exitCrate(self, ctx: RustyParser.CrateContext):
        self.tree[ctx] = ''
        if ctx.item() is None:
            return super().exitCrate(ctx)

        if 'main' not in self.functions:
            raise Exception # no start function defined

        program = [
            finstr('call main'),
            finstr('stop')
        ]
        program.extend(map(self.tree.get, ctx.item()))
        self.tree[ctx] = '\n'.join(program)
        return super().exitCrate(ctx)
