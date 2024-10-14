#!/usr/bin/env python3
from libs.RustyListener import RustyListener
from libs.RustyParser import RustyParser


def finstr(ins: str) -> str:
    return '\t' + ins

class FERListener(RustyListener):
    def __init__(self):
        super().__init__()
        self.tree = {}
        self.states = []

# Implement negation_ops alternatives
    def exitArithmeticNegation(self, ctx: RustyParser.ArithmeticNegationContext):
        self.tree[ctx] = finstr('neg')
        return super().exitArithmeticNegation(ctx)

    def exitLogicNegation(self, ctx: RustyParser.LogicNegationContext):
        self.tree[ctx] = finstr('not')
        return super().exitLogicNegation(ctx)

# Implement arithmetic_or_logical_ops alternatives
    def exitMulBinop(self, ctx: RustyParser.MulBinopContext):
        self.tree[ctx] = finstr('mul')
        return super().exitMulBinop(ctx)

    def exitDivBinop(self, ctx: RustyParser.DivBinopContext):
        self.tree[ctx] = finstr('div')
        return super().exitDivBinop(ctx)

    def exitModBinop(self, ctx: RustyParser.ModBinopContext):
        self.tree[ctx] = finstr('mod')
        return super().exitModBinop(ctx)

    def exitAddBinop(self, ctx: RustyParser.AddBinopContext):
        self.tree[ctx] = finstr('add')
        return super().exitAddBinop(ctx)

    def exitSubBinop(self, ctx: RustyParser.SubBinopContext):
        self.tree[ctx] = finstr('sub')
        return super().exitSubBinop(ctx)

    def exitShlBinop(self, ctx: RustyParser.ShlBinopContext):
        self.tree[ctx] = finstr('shl')
        return super().exitShlBinop(ctx)

    def exitShrBinop(self, ctx: RustyParser.ShrBinopContext):
        self.tree[ctx] = finstr('shr')
        return super().exitShrBinop(ctx)

    def exitBitwiseAndBinop(self, ctx: RustyParser.BitwiseAndBinopContext):
        self.tree[ctx] = finstr('and')
        return super().exitBitwiseAndBinop(ctx)

    def exitBitwiseXorBinop(self, ctx: RustyParser.BitwiseXorBinopContext):
        self.tree[ctx] = finstr('xor')
        return super().exitBitwiseXorBinop(ctx)

    def exitBitwiseOrBinop(self, ctx: RustyParser.BitwiseOrBinopContext):
        self.tree[ctx] = finstr('or')
        return super().exitBitwiseOrBinop(ctx)

# Implement comparison_ops alternatives
    def exitEqBinop(self, ctx: RustyParser.EqBinopContext):
        self.tree[ctx] = '\n'.join(map(finstr, [
            'cmp',
            'push 0',
            'cmp'
        ]))
        return super().exitEqBinop(ctx)

    def exitNEBinop(self, ctx: RustyParser.NEBinopContext):
        self.tree[ctx] = '\n'.join(map(finstr, [
            'cmp',
            'push 0',
            'cmp',
            'not'
        ]))
        return super().exitNEBinop(ctx)

    def exitGTBinop(self, ctx: RustyParser.GTBinopContext):
        raise NotImplementedError
        return super().exitGTBinop(ctx)

    def exitLTBinop(self, ctx: RustyParser.LTBinopContext):
        raise NotImplementedError
        return super().exitLTBinop(ctx)

    def exitGEBinop(self, ctx: RustyParser.GEBinopContext):
        raise NotImplementedError
        return super().exitGEBinop(ctx)

    def exitLEBinop(self, ctx: RustyParser.LEBinopContext):
        raise NotImplementedError
        return super().exitLEBinop(ctx)

# Implement lazy_boolean_ops alternatives
    def exitBooleanAndBinop(self, ctx: RustyParser.BooleanAndBinopContext):
        self.tree[ctx] = finstr('and')
        return super().exitBooleanAndBinop(ctx)

    def exitBooleanOrBinop(self, ctx: RustyParser.BooleanOrBinopContext):
        self.tree[ctx] = finstr('or')
        return super().exitBooleanOrBinop(ctx)

# Implement binary_ops alternatives
    def exitALBinops(self, ctx: RustyParser.ALBinopsContext):
        self.tree[ctx] = self.tree[ctx.arithmetic_or_logical_ops()]
        return super().exitALBinops(ctx)

    def exitCMPBinops(self, ctx: RustyParser.CMPBinopsContext):
        self.tree[ctx] = self.tree[ctx.comparison_ops()]
        return super().exitCMPBinops(ctx)

    def exitLazyBooleanBinops(self, ctx: RustyParser.LazyBooleanBinopsContext):
        self.tree[ctx] = self.tree[ctx.lazy_boolean_ops()]
        return super().exitLazyBooleanBinops(ctx)

    def exitCall_params(self, ctx: RustyParser.Call_paramsContext):
        self.tree[ctx] = '\n'.join(map(self.tree.get, ctx.expression()))
        return super().exitCall_params(ctx)

# Implement if_expression rule
    def enterElseBlockExpr(self, ctx: RustyParser.ElseBlockExprContext):
        self.states.append(False)
        return super().enterElseBlockExpr(ctx)

    def exitElseBlockExpr(self, ctx: RustyParser.ElseBlockExprContext):
        self.states.pop()
        self.tree[ctx] = self.tree[ctx.block_expression()]
        return super().exitElseBlockExpr(ctx)

    def enterElifExpr(self, ctx: RustyParser.ElifExprContext):
        self.states.append(False)
        return super().enterElifExpr(ctx)

    def exitElifExpr(self, ctx: RustyParser.ElifExprContext):
        self.states.pop()
        self.tree[ctx] = self.tree[ctx.if_expression()]
        return super().exitElifExpr(ctx)

    def exitIf_expression(self, ctx: RustyParser.If_expressionContext):
        fi_label = 'fi_label'
        else_branch_label = fi_label if ctx.else_branch() is None else 'else_branch_label'

        instructions = [
            self.tree[ctx.expression()],
            finstr('jnz ' + else_branch_label),
            self.tree[ctx.block_expression()]
        ]
        if ctx.else_branch() is not None:
            instructions.append(finstr('jmp ' + fi_label))
            instructions.append(self.tree[ctx.else_branch()])
        instructions.append(fi_label + ':')

        self.tree[ctx] = '\n'.join(instructions)
        return super().exitIf_expression(ctx)

# Implement expression_with_block alternatives
    def enterBlockExpr(self, ctx: RustyParser.BlockExprContext):
        self.states.append(False)
        return super().enterBlockExpr(ctx)

    def exitBlockExpr(self, ctx: RustyParser.BlockExprContext):
        self.states.pop()
        self.tree[ctx] = self.tree[ctx.block_expression()]
        return super().exitBlockExpr(ctx)

    def enterInfiniteLoop(self, ctx: RustyParser.InfiniteLoopContext):
        self.states.append(False)
        return super().enterInfiniteLoop(ctx)

    def exitInfiniteLoop(self, ctx: RustyParser.InfiniteLoopContext):
        self.states.pop()
        loop_enter_label = 'inf_loop_enter_label'
        loop_exit_label = 'inf_loop_exit_label'
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.block_expression()],
            finstr('jmp ' + loop_enter_label),
            loop_exit_label + ':'
        ])
        return super().exitInfiniteLoop(ctx)

    def enterWhileLoop(self, ctx: RustyParser.WhileLoopContext):
        self.states.append(False)
        return super().enterWhileLoop(ctx)

    def exitWhileLoop(self, ctx: RustyParser.WhileLoopContext):
        self.states.pop()
        loop_enter_label = 'while_loop_enter_label'
        loop_exit_label = 'while_loop_exit_label'
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.expression()],
            finstr('jnz ' + loop_exit_label),
            self.tree[ctx.block_expression()],
            finstr('jmp ' + loop_enter_label),
            loop_exit_label + ':'
        ])
        return super().exitWhileLoop(ctx)

    def enterForLoop(self, ctx: RustyParser.ForLoopContext):
        self.states.append(False)
        return super().enterForLoop(ctx)

    def exitForLoop(self, ctx: RustyParser.ForLoopContext):
        self.states.pop()
        raise NotImplementedError
        return super().exitForLoop(ctx)

    def enterIfExpr(self, ctx: RustyParser.IfExprContext):
        self.states.append(False)
        return super().enterIfExpr(ctx)

    def exitIfExpr(self, ctx: RustyParser.IfExprContext):
        self.states.pop()
        self.tree[ctx] = self.tree[ctx.if_expression()]
        return super().exitIfExpr(ctx)

    def exitLet_statement(self, ctx: RustyParser.Let_statementContext):
        expr = ctx.expression()
        self.tree[ctx] = '' if expr is None else expr
        return super().exitLet_statement(ctx)

# Implement expression alternatives
    def exitTrueLiteral(self, ctx: RustyParser.TrueLiteralContext):
        self.tree[ctx] = finstr('push 1')
        return super().exitTrueLiteral(ctx)

    def exitFalseLiteral(self, ctx: RustyParser.FalseLiteralContext):
        self.tree[ctx] = finstr('push 0')
        return super().exitFalseLiteral(ctx)

    def exitIntegerLiteral(self, ctx: RustyParser.IntegerLiteralContext):
        self.tree[ctx] = finstr('push ' + str(ctx.INTEGER_LITERAL()))
        return super().exitIntegerLiteral(ctx)

    def exitFloatLiteral(self, ctx: RustyParser.FloatLiteralContext):
        self.tree[ctx] = finstr('push ' + str(ctx.FLOAT_LITERAL()))
        return super().exitFloatLiteral(ctx)

    def exitPathExpr(self, ctx: RustyParser.PathExprContext):
        self.tree[ctx] = finstr('push ' + str(ctx.IDENTIFIER()))
        return super().exitPathExpr(ctx)

    def exitGroupedExpr(self, ctx: RustyParser.GroupedExprContext):
        self.tree[ctx] = self.tree[ctx.expression()]
        return super().exitGroupedExpr(ctx)

    def exitCallExpr(self, ctx: RustyParser.CallExprContext):
        instructions = []
        if ctx.call_params() is not None:
            instructions.append(self.tree[ctx.call_params()])
        instructions.append(finstr('call ' + str(ctx.IDENTIFIER())))

        self.tree[ctx] = '\n'.join(instructions)
        return super().exitCallExpr(ctx)

    def exitUnaryExpr(self, ctx: RustyParser.UnaryExprContext):
        self.tree[ctx] = '\n'.join(map(self.tree.get,
                                       [ctx.expression(), ctx.negation_ops()]))
        return super().exitUnaryExpr(ctx)

    def exitBinaryExpr(self, ctx: RustyParser.BinaryExprContext):
        self.tree[ctx] = '\n'.join(map(self.tree.get,
                                       ctx.expression() + [ctx.binary_ops()]))
        return super().exitBinaryExpr(ctx)

    def exitReturnExpr(self, ctx: RustyParser.ReturnExprContext):
        instructions = []
        if ctx.expression() is not None:
            instructions.append(self.tree[ctx.expression()])
        instructions.append(finstr('ret'))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitReturnExpr(ctx)

    def exitExprWithBlock(self, ctx: RustyParser.ExprWithBlockContext):
        self.tree[ctx] = self.tree[ctx.getChild()]
        return super().exitExprWithBlock(ctx)

# Implement expression_statement
    def exitExpression_statement(self, ctx: RustyParser.Expression_statementContext):
        if ctx.expression() is not None:
            self.tree[ctx] = self.tree[ctx.expression()]
        elif ctx.expression_with_block() is not None:
            self.tree[ctx] = self.tree[ctx.expression_with_block()]
        else:
            raise Exception # malformed parse rules

        return super().exitExpression_statement(ctx)

# Implement statement alternatives
    def exitStLetStatement(self, ctx: RustyParser.StLetStatementContext):
        self.tree[ctx] = self.tree[ctx.let_statement()]
        return super().exitStLetStatement(ctx)

    def exitStExprStatement(self, ctx: RustyParser.StExprStatementContext):
        self.tree[ctx] = self.tree[ctx.expression_statement()]
        return super().exitStExprStatement(ctx)

    def exitStNopStatement(self, ctx: RustyParser.StNopStatementContext):
        self.tree[ctx] = finstr('nop')
        return super().exitStNopStatement(ctx)

    def exitStatements(self, ctx: RustyParser.StatementsContext):
        instructions = []
        if ctx.statement() is not None:
            instructions.extend(map(self.tree.get, ctx.statement()))
        if ctx.expression() is not None:
            instructions.append(self.tree[ctx.expression()])
            if self.states[-1]:
                instructions.append(finstr('ret'))
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitStatements(ctx)

# Implement block_expression
    def exitBlock_expression(self, ctx: RustyParser.Block_expressionContext):
        statements = ctx.statements()
        self.tree[ctx] = '' if statements is None else self.tree[statements]
        return super().exitBlock_expression(ctx)

    def enterBlock_expression(self, ctx: RustyParser.Block_expressionContext):
        # self.scopes.append('block_expression')
        return super().enterBlock_expression(ctx)

# Implement function rule
    def enterFunction(self, ctx: RustyParser.FunctionContext):
        self.states.append(True)
        return super().enterFunction(ctx)

    def exitFunction(self, ctx: RustyParser.FunctionContext):
        self.states.pop()
        self.tree[ctx] = '\n'.join([
            str(ctx.IDENTIFIER()) + ':',
            self.tree[ctx.block_expression()]
        ])
        return super().exitFunction(ctx)

# Implement root rules (crate and item)
    def exitItem(self, ctx: RustyParser.ItemContext):
        self.tree[ctx] = self.tree[ctx.function()]
        return super().exitItem(ctx)

    def exitCrate(self, ctx: RustyParser.CrateContext):
        self.tree[ctx] = '' if ctx.item() is None else '\n'.join(map(self.tree.get,
                                                                     ctx.item()))
        return super().exitCrate(ctx)
