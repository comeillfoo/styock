#!/usr/bin/env python3
from enum import IntEnum, auto
from typing import Tuple
from functools import reduce


from libs.RustyListener import RustyListener
from libs.RustyParser import RustyParser


class FERTypes(IntEnum):
    BOOLEAN = 0
    INT8 = auto()
    UINT8 = auto()
    INT16 = auto()
    UINT16 = auto()
    INT32 = auto()
    UINT32 = auto()
    INT64 = auto()
    UINT64 = auto()
    ISIZE = auto()
    USIZE = auto()
    INT128 = auto()
    UINT128 = auto()
    FLOAT32 = auto()
    FLOAT64 = auto()
    TUPLE = auto()

    @classmethod
    def from_str_suffix(cls, idx: int, suffix: str):
        table = {
            '8':    [cls.INT8,   cls.UINT8],
            '16':   [cls.INT16,  cls.UINT16],
            '32':   [cls.INT32,  cls.UINT32, cls.FLOAT32],
            '64':   [cls.INT64,  cls.UINT64, cls.FLOAT64],
            '128':  [cls.INT128, cls.UINT128],
            'size': [cls.ISIZE,  cls.USIZE]
        }
        if suffix not in table:
            raise Exception # unknown type
        try:
            return table[suffix][idx]
        except IndexError:
            raise Exception # unsupported bit depth


    @classmethod
    def from_ctx(cls, ctx: RustyParser.TypeContext):
        raw_type = ctx.BOOL_TYPE()
        if raw_type is not None:
            return cls.BOOLEAN
        raw_type = ctx.UINT_TYPES()
        if raw_type is not None:
            return cls.from_str_suffix(1, raw_type.lstrip('u'))
        raw_type = ctx.SINT_TYPES()
        if raw_type is not None:
            return cls.from_str_suffix(0, raw_type.lstrip('i'))
        raw_type = ctx.FLOAT_TYPES()
        if raw_type is not None:
            return cls.from_str_suffix(2, raw_type.lstrip('f'))
        raw_type = ctx.tuple_type()
        if raw_type is None:
            raise Exception # unsupported type
        return cls.TUPLE


class FERFunctionParam:
    def __init__(self, param_name: str, param_type: FERTypes):
        self.param_name = param_name
        self.param_type = param_type


    @classmethod
    def from_function_param_ctx(cls, ctx: RustyParser.Function_paramContext):
        return cls(ctx.IDENTIFIER(), FERTypes.from_ctx(ctx.type_()))


class FRFunction:
    def __init__(self, name: str, params: list):
        self.name = name
        self.params = params


    @classmethod
    def from_parser_ctx(cls, ctx: RustyParser.FunctionContext):
        params = ctx.function_parameters()
        def _fold(acc: Tuple[list[FERFunctionParam], set[str]],
                  ctx: RustyParser.Function_paramContext
                  ) -> Tuple[list[FERFunctionParam], set[str]]:
            param = FERFunctionParam.from_function_param_ctx(ctx)
            if param.param_name in acc[1]:
                raise Exception # duplicate identifier in parameters
            acc[1].add(param.param_name)
            acc[0].append(param)
            return acc
        params = reduce(_fold, [] if params is None else params.function_param(), [])
        print(params)
        return cls(ctx.IDENTIFIER(), params)


class FERListener(RustyListener):
    def __init__(self):
        super().__init__()
        self.tree = {}

# Implement negation_ops alternatives
    def exitArithmeticNegation(self, ctx: RustyParser.ArithmeticNegationContext):
        self.tree[ctx] = 'neg'
        return super().exitArithmeticNegation(ctx)

    def exitLogicNegation(self, ctx: RustyParser.LogicNegationContext):
        self.tree[ctx] = 'not'
        return super().exitLogicNegation(ctx)

# Implement arithmetic_or_logical_ops alternatives
    def exitMulBinop(self, ctx: RustyParser.MulBinopContext):
        self.tree[ctx] = 'mul'
        return super().exitMulBinop(ctx)

    def exitDivBinop(self, ctx: RustyParser.DivBinopContext):
        self.tree[ctx] = 'div'
        return super().exitDivBinop(ctx)

    def exitModBinop(self, ctx: RustyParser.ModBinopContext):
        self.tree[ctx] = 'mod'
        return super().exitModBinop(ctx)

    def exitAddBinop(self, ctx: RustyParser.AddBinopContext):
        self.tree[ctx] = 'add'
        return super().exitAddBinop(ctx)

    def exitSubBinop(self, ctx: RustyParser.SubBinopContext):
        self.tree[ctx] = 'sub'
        return super().exitSubBinop(ctx)

    def exitShlBinop(self, ctx: RustyParser.ShlBinopContext):
        self.tree[ctx] = 'shl'
        return super().exitShlBinop(ctx)

    def exitShrBinop(self, ctx: RustyParser.ShrBinopContext):
        self.tree[ctx] = 'shr'
        return super().exitShrBinop(ctx)

    def exitBitwiseAndBinop(self, ctx: RustyParser.BitwiseAndBinopContext):
        self.tree[ctx] = 'and'
        return super().exitBitwiseAndBinop(ctx)

    def exitBitwiseXorBinop(self, ctx: RustyParser.BitwiseXorBinopContext):
        self.tree[ctx] = 'xor'
        return super().exitBitwiseXorBinop(ctx)

    def exitBitwiseOrBinop(self, ctx: RustyParser.BitwiseOrBinopContext):
        self.tree[ctx] = 'or'
        return super().exitBitwiseOrBinop(ctx)

# Implement comparison_ops alternatives
    def exitEqBinop(self, ctx: RustyParser.EqBinopContext):
        self.tree[ctx] = '\n'.join([
            'cmp',
            'push 0',
            'cmp'
        ])
        return super().exitEqBinop(ctx)

    def exitNEBinop(self, ctx: RustyParser.NEBinopContext):
        self.tree[ctx] = '\n'.join([
            'cmp',
            'push 0',
            'cmp',
            'not'
        ])
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
        self.tree[ctx] = 'and'
        return super().exitBooleanAndBinop(ctx)

    def exitBooleanOrBinop(self, ctx: RustyParser.BooleanOrBinopContext):
        self.tree[ctx] = 'or'
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

# Implement expression alternatives
    def exitTrueLiteral(self, ctx: RustyParser.TrueLiteralContext):
        self.tree[ctx] = '1'
        return super().exitTrueLiteral(ctx)

    def exitFalseLiteral(self, ctx: RustyParser.FalseLiteralContext):
        self.tree[ctx] = '0'
        return super().exitFalseLiteral(ctx)

    def exitIntegerLiteral(self, ctx: RustyParser.IntegerLiteralContext):
        self.tree[ctx] = str(ctx.INTEGER_LITERAL())
        return super().exitIntegerLiteral(ctx)

    def exitFloatLiteral(self, ctx: RustyParser.FloatLiteralContext):
        self.tree[ctx] = str(ctx.FLOAT_LITERAL())
        return super().exitFloatLiteral(ctx)

    def exitPathExpr(self, ctx: RustyParser.PathExprContext):
        self.tree[ctx] = str(ctx.IDENTIFIER())
        return super().exitPathExpr(ctx)

    def exitGroupedExpr(self, ctx: RustyParser.GroupedExprContext):
        self.tree[ctx] = self.tree[ctx.expression()]
        return super().exitGroupedExpr(ctx)

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
        instructions.append('ret')
        self.tree[ctx] = '\n'.join(instructions)
        return super().exitReturnExpr(ctx)

    def exitExprWithBlock(self, ctx: RustyParser.ExprWithBlockContext):
        self.tree[ctx] = self.tree[ctx.getChild()]
        return super().exitExprWithBlock(ctx)

# Implement expression_with_block alternatives
    def exitBlockExpr(self, ctx: RustyParser.BlockExprContext):
        self.tree[ctx] = self.tree[ctx.block_expression()]
        return super().exitBlockExpr(ctx)

    def exitInfiniteLoop(self, ctx: RustyParser.InfiniteLoopContext):
        loop_enter_label = 'inf_loop_enter_label'
        loop_exit_label = 'inf_loop_exit_label'
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.block_expression()],
            'jmp' + loop_enter_label,
            loop_exit_label + ':'
        ])
        return super().exitInfiniteLoop(ctx)

    def exitWhileLoop(self, ctx: RustyParser.WhileLoopContext):
        loop_enter_label = 'while_loop_enter_label'
        loop_exit_label = 'while_loop_exit_label'
        self.tree[ctx] = '\n'.join([
            loop_enter_label + ':',
            self.tree[ctx.expression()],
            'jnz' + loop_exit_label,
            self.tree[ctx.block_expression()],
            'jmp' + loop_enter_label,
            loop_exit_label + ':'
        ])
        return super().exitWhileLoop(ctx)

    def exitForLoop(self, ctx: RustyParser.ForLoopContext):
        raise NotImplementedError
        return super().exitForLoop(ctx)

    def exitIfExpr(self, ctx: RustyParser.IfExprContext):
        self.tree[ctx] = self.tree[ctx.if_expression()]
        return super().exitIfExpr(ctx)

# Implement block_expression
    def exitBlock_expression(self, ctx: RustyParser.Block_expressionContext):
        # TODO: fix errors
        statements = ctx.statements()
        statements = [] if statements is None else statements.statement()
        self.tree[ctx] = '\n'.join(map(self.tree.get, statements))
        return super().exitBlock_expression(ctx)

# Implement if_expression rule
    def exitElseBlockExpr(self, ctx: RustyParser.ElseBlockExprContext):
        self.tree[ctx] = self.tree[ctx.block_expression()]
        return super().exitElseBlockExpr(ctx)

    def exitElifExpr(self, ctx: RustyParser.ElifExprContext):
        self.tree[ctx] = self.tree[ctx.if_expression()]
        return super().exitElifExpr(ctx)

    def exitIf_expression(self, ctx: RustyParser.If_expressionContext):
        fi_label = 'fi_label'
        else_branch_label = fi_label if ctx.else_branch() is None else 'else_branch_label'

        instructions = [
            self.tree[ctx.expression()],
            'jnz' + else_branch_label,
            self.tree[ctx.block_expression()]
        ]
        if ctx.else_branch() is not None:
            instructions.append('jmp' + fi_label)
            instructions.append(self.tree[ctx.else_branch()])

        self.tree[ctx] = '\n'.join(instructions)
        return super().exitIf_expression(ctx)
