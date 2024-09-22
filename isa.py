#!/usr/bin/env python3
from abc import ABC, abstractmethod

import traps


class Context:
    def __init__(self):
        self.stack = []
        self.ip = 0


class Instruction(ABC):
    @abstractmethod
    def execute(self, ctx: Context) -> bool:
        raise NotImplementedError


class Push(Instruction):
    def __init__(self, arg: int):
        self.arg = arg

    def execute(self, ctx: Context) -> bool:
        ctx.stack.append(self.arg)
        return False


class Pop(Instruction):
    def execute(self, ctx: Context) -> bool:
        try:
            ctx.stack.pop()
        except IndexError:
            raise traps.StackUnderflowTrap
        return False


class Swap(Instruction):
    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(a)
            ctx.stack.append(b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False


class Duplicate(Instruction):
    def execute(self, ctx: Context) -> bool:
        if len(ctx.stack) == 0:
            raise traps.StackUnderflowTrap

        arg = ctx.stack[-1]
        ctx.stack.append(arg)
        return False


class Stop(Instruction):
    def execute(self, ctx: Context) -> bool:
        return True


class Add(Instruction):
    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(a + b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False
# TODO: Sub, Mul, Div, Mod, Neg, And, Or, Not and etc...


class Compare(Instruction):
    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(1 if a > b else (-1 if a < b else 0))
        except IndexError:
            raise traps.StackUnderflowTrap
        return False


class Jump(Instruction):
    def __init__(self, arg: int):
        self.arg = arg


    def execute(self, ctx: Context) -> bool:
        ctx.ip += self.arg
        return False

