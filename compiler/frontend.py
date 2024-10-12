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
    def __init__(self, out):
        super().__init__()
        self.functions = {}
        self.out = out


    def exitFunction(self, ctx: RustyParser.FunctionContext):
        function = FRFunction.from_parser_ctx(ctx)
        if function.name in self.functions:
            raise Exception # function is already defined

        self.functions[function.name] = function
        print(function.name, ':', sep='', file=self.out)
        print(file=self.out)
        return super().exitFunction(ctx)


    def exitUnsignedIntegerType(self, ctx: RustyParser.UnsignedIntegerTypeContext):
        return super().exitUnsignedIntegerType(ctx)

    def exitSignedIntegerType(self, ctx: RustyParser.SignedIntegerTypeContext):
        return super().exitSignedIntegerType(ctx)

    def exitFloatType(self, ctx: RustyParser.FloatTypeContext):
        return super().exitFloatType(ctx)

    def exitBooleanType(self, ctx: RustyParser.BooleanTypeContext):
        return super().exitBooleanType(ctx)

    def exitTupleType(self, ctx: RustyParser.TupleTypeContext):
        return super().exitTupleType(ctx)
