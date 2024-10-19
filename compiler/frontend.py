#!/usr/bin/env python3
from typing import Optional
from dataclasses import dataclass

from libs.RustyListener import RustyListener
from libs.RustyParser import RustyParser


@dataclass
class VariableMeta:
    identifier: int = 0
    mutable: bool = False

@dataclass
class FnMeta:
    name: str
    parameters: dict[str, VariableMeta]
    locals: dict[str, VariableMeta]


def finstr(ins: str) -> str:
    return '\t' + ins


class FERListener(RustyListener):
    def __init__(self):
        super().__init__()
        self.tree = {}
        self.functions: dict[str, FnMeta] = {}
        self.counter = 0
        self.current_function: Optional[str] = None

    def next_label(self, prefix: str) -> str:
        self.counter += 1
        return f'{self.counter}_{prefix}'

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
        self.tree[ctx] = finstr(instruction)
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
        fi_label = self.next_label('fi_label')
        else_branch_label = fi_label
        if ctx.elseBranch() is not None:
            else_branch_label = self.next_label('else_branch_label')

        instructions = [
            self.tree[ctx.expression()],
            finstr('jift ' + else_branch_label),
            self.tree[ctx.blockExpression()]
        ]
        if ctx.elseBranch() is not None:
            instructions.append(finstr('jmp ' + fi_label))
            instructions.append(self.tree[ctx.elseBranch()])
        instructions.append(fi_label + ':')

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

    def exitInfiniteLoopExpr(self, ctx: RustyParser.InfiniteLoopExprContext):
        loop_enter_label = self.next_label('inflo_enter_label')
        loop_exit_label = self.next_label('inflo_exit_label')
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.blockExpression()],
            finstr('jmp ' + loop_enter_label),
            loop_exit_label + ':'
        ])
        return super().exitInfiniteLoopExpr(ctx)

    def exitPredicateLoopExpr(self, ctx: RustyParser.PredicateLoopExprContext):
        loop_enter_label = self.next_label('predlo_enter_label')
        loop_exit_label = self.next_label('predlo_exit_label')
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.expression()],
            finstr('jift ' + loop_exit_label),
            self.tree[ctx.blockExpression()],
            finstr('jmp ' + loop_enter_label),
            loop_exit_label + ':'
        ])
        return super().exitPredicateLoopExpr(ctx)

    def exitIfExpr(self, ctx: RustyParser.IfExprContext):
        self.tree[ctx] = self.tree[ctx.ifExpression()]
        return super().exitIfExpr(ctx)

# Implement expression alternatives
    def exitIntegerLiteral(self, ctx: RustyParser.IntegerLiteralContext):
        self.tree[ctx] = finstr('push ' + str(ctx.INTEGER_LITERAL()))
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
            self.tree[ctx.expression()],
            finstr(f'load {variable.identifier}'),
            self.tree[ctx.compoundAssignOps()],
            finstr(f'store {variable.identifier}')
        ])
        return super().exitCompoundAssignmentExpr(ctx)

    # TODO: break and continue
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
        def _list_parameters(ctx: RustyParser.FunctionContext) -> dict[str, int]:
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
        self.tree[ctx] = '' if ctx.item() is None else '\n'.join(map(self.tree.get,
                                                                     ctx.item()))
        return super().exitCrate(ctx)
