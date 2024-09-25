#!/usr/bin/env python3
from abc import ABC, abstractmethod
from enum import IntEnum, auto
import numpy as np

import traps


class Opcode(IntEnum):
    NOP = 0
    PUSH = auto()
    POP = auto()
    SWAP = auto()
    DUP = auto()
    STOP = auto()
    ADD = auto()
    # TODO: SUB, MUL, DIV, MOD, NEG, AND, OR, NOT and etc...
    CMP = auto()
    JMP = auto()
    # TODO: JZ, JNZ, JGT and etc...
    CALL = auto()
    RET = auto()
    _MAXOP = auto()


class Context:
    def __init__(self):
        self.stack = []
        self.ip = np.uint64(0)


class Instruction(ABC):
    @abstractmethod
    def opcode(self) -> Opcode:
        raise NotImplementedError

    @abstractmethod
    def args(self) -> list[np.uint64]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, ctx: Context) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def nargs(cls) -> int:
        raise NotImplementedError


class NoOperation(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.NOP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Push(Instruction):
    def __init__(self, arg: int):
        self.arg = np.uint64(arg)

    def opcode(self) -> Opcode:
        return Opcode.PUSH

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.stack.append(self.arg)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Pop(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.POP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            ctx.stack.pop()
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Swap(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.SWAP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(a)
            ctx.stack.append(b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Duplicate(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.DUP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        if len(ctx.stack) == 0:
            raise traps.StackUnderflowTrap

        arg = ctx.stack[-1]
        ctx.stack.append(arg)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Stop(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.STOP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        return True

    @classmethod
    def nargs(cls) -> int:
        return 0


class Add(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.ADD

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(a + b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0
# TODO: Sub, Mul, Div, Mod, Neg, And, Or, Not and etc...


class Compare(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.CMP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.stack.pop()
            b = ctx.stack.pop()
            ctx.stack.append(a - b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Jump(Instruction):
    def __init__(self, arg: np.uint64):
        self.arg = arg

    def opcode(self) -> Opcode:
        return Opcode.JMP

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.ip += self.arg
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1
# TODO: conditional branches


class Call(Instruction):
    def __init__(self, arg: np.uint64):
        self.arg = arg

    def opcode(self) -> Opcode:
        return Opcode.CALL

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.stack.append(ctx.ip)
        ctx.ip += self.arg
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Ret(Instruction):
    def opcode(self) -> Opcode:
        return Opcode.RET

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            return_address = ctx.stack.pop()
            ctx.ip = return_address
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


INSTRUCTIONS_MAP = {
    Opcode.NOP: NoOperation,
    Opcode.PUSH: Push,
    Opcode.POP: Pop,
    Opcode.SWAP: Swap,
    Opcode.DUP: Duplicate,
    Opcode.STOP: Stop,
    Opcode.ADD: Add,
    Opcode.CMP: Compare,
    Opcode.JMP: Jump,
    Opcode.CALL: Call,
    Opcode.RET: Ret
}
