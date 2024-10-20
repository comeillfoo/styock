#!/usr/bin/env python3
from abc import ABC, abstractmethod
from enum import IntEnum, auto
import numpy as np

from . import traps


class Opcode(IntEnum):
    NOP = 0
    PUSH = auto()
    POP = auto()
    SWAP = auto()
    DUP = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    SHL = auto()
    SHR = auto()
    MAX = auto()
    MIN = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    INC = auto()
    DEC = auto()
    NEG = auto()
    NOT = auto()
    LT = auto()
    LE = auto()
    EQ = auto()
    NEQ = auto()
    GE = auto()
    GT = auto()
    LOAD = auto()
    STORE = auto()
    CALL = auto()
    RET = auto()
    JMP = auto()
    JIFT = auto()
    STOP = auto()
    _MAXOP = auto()


class Frame:
    def __init__(self, return_address: np.uint64):
        self.return_address = return_address
        self.variables = {}


class Context:
    def __init__(self):
        self.operands_stack = []
        self.frames = []
        self.ip = np.uint64(0)


def force_uint64(number: int) -> np.uint64:
    if number < 0:
        number += (1 << 64)
    if number >= (1 << 64):
        number &= (1 << 64) - 1
    return np.uint64(number)


class Instruction(ABC):
    @classmethod
    @abstractmethod
    def opcode(cls) -> Opcode:
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

    def __repr__(self) -> str:
        components = [type(self).__name__]
        if self.nargs() > 0:
            components.append('(')
            components.append(', '.join(map(hex, self.args())))
            components.append(')')
        return ''.join(components)


class NoOperation(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
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
        self.arg = force_uint64(arg)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.PUSH

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.operands_stack.append(self.arg)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Pop(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.POP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            ctx.operands_stack.pop()
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Swap(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SWAP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.operands_stack.pop()
            b = ctx.operands_stack.pop()
            ctx.operands_stack.append(a)
            ctx.operands_stack.append(b)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Duplicate(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.DUP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        if len(ctx.operands_stack) == 0:
            raise traps.StackUnderflowTrap

        arg = ctx.operands_stack[-1]
        ctx.operands_stack.append(arg)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class BinaryApplyInstruction(Instruction):
    @abstractmethod
    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        raise NotImplementedError

    def execute(self, ctx: Context) -> bool:
        try:
            b = ctx.operands_stack.pop()
            a = ctx.operands_stack.pop()
            ctx.operands_stack.append(self._apply(a, b))
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    def args(self) -> list[np.uint64]:
        return []

    @classmethod
    def nargs(cls) -> int:
        return 0

class Add(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.ADD

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a + b

class Substract(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SUB

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a - b

class Multiply(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MUL

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a * b

class Divide(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.DIV

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        if b == 0:
            raise traps.ZeroDivisionTrap
        return a / b

class Modulo(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MOD

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        if b == 0:
            raise traps.ZeroDivisionTrap
        return a % b

class ShiftLeft(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SHL

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a << b

class ShiftRight(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SHR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a >> b


class Maximum(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MAX

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a if a > b else b

class Minimum(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MIN

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a if a < b else b

class And(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.AND

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a & b

class Or(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.OR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a | b

class Xor(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.XOR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a ^ b


class UnaryApplyInstruction(Instruction):
    @abstractmethod
    def _apply(self, a: np.uint64) -> np.uint64:
        raise NotImplementedError

    def execute(self, ctx: Context) -> bool:
        try:
            a = ctx.operands_stack.pop()
            ctx.operands_stack.append(a)
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    def args(self) -> list[np.uint64]:
        return []

    @classmethod
    def nargs(cls) -> int:
        return 0

class Increment(UnaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.INC

    def _apply(self, a: np.uint64) -> np.uint64:
        return a + 1

class Decrement(UnaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.DEC

    def _apply(self, a: np.uint64) -> np.uint64:
        return a - 1

class Negate(UnaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NEG

    def _apply(self, a: np.uint64) -> np.uint64:
        return -a

class Not(UnaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NOT

    def _apply(self, a: np.uint64) -> np.uint64:
        return ~a


class LessThan(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LT

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a < b else 0

class LessOrEqual(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LE

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a <= b else 0

class Equal(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.EQ

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a == b else 0

class NotEqual(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NEQ

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a != b else 0

class GreaterThan(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.GT

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a > b else 0

class GreaterOrEqual(BinaryApplyInstruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.GE

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a >= b else 0


class Load(Instruction):
    def __init__(self, variable_id: int):
        self.variable_id = force_uint64(variable_id)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LOAD

    def args(self) -> list[np.uint64]:
        return [self.variable_id]

    def execute(self, ctx: Context) -> bool:
        variable_value = ctx.frames[-1].variables.get(self.variable_id, 0)
        ctx.operands_stack.append(variable_value)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Store(Instruction):
    def __init__(self, variable_id: int):
        self.variable_id = force_uint64(variable_id)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.STORE

    def args(self) -> list[np.uint64]:
        return [self.variable_id]

    def execute(self, ctx: Context) -> bool:
        try:
            variable_value = ctx.operands_stack.pop()
            ctx.frames[-1].variables[self.variable_id] = variable_value
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Call(Instruction):
    def __init__(self, arg: int):
        self.arg = force_uint64(arg)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.CALL

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.frames.append(Frame(ctx.ip))
        ctx.ip = ctx.ip - 1 + self.arg
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Return(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.RET

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        try:
            frame = ctx.frames.pop()
            ctx.ip = frame.return_address
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 0


class Jump(Instruction):
    def __init__(self, arg: int):
        self.arg = force_uint64(arg)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.JMP

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        ctx.ip = ctx.ip - 1 + self.arg
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1

class JumpIfTrue(Instruction):
    def __init__(self, arg: int):
        self.arg = force_uint64(arg)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.JIFT

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        try:
            cond = ctx.operands_stack.pop()
            if cond != 0:
                ctx.ip = ctx.ip - 1 + self.arg
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Stop(Instruction):
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.STOP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        return True

    @classmethod
    def nargs(cls) -> int:
        return 0


INSTRUCTIONS_MAP = {
    instruction.opcode(): instruction for instruction in [
        NoOperation,
        Push,
        Pop,
        Swap,
        Duplicate,
        Add,
        Substract,
        Multiply,
        Divide,
        Modulo,
        ShiftLeft,
        ShiftRight,
        Maximum,
        Minimum,
        And,
        Or,
        Xor,
        Increment,
        Decrement,
        Negate,
        Not,
        LessThan,
        LessOrEqual,
        Equal,
        NotEqual,
        GreaterThan,
        GreaterOrEqual,
        Load,
        Store,
        Call,
        Return,
        Jump,
        JumpIfTrue,
        Stop,
    ]
}
