#!/usr/bin/env python3
'''Реализация инструкций стековой виртуальной машины и обслуживающих ее структур:

+ контекст вычислений - стек операндов, стек фреймов и указатель инструкций (IP);
+ фрейм - хранилище локальных для фрейма переменных и их значений, адрес возврата из фрейма

Фрейм используется для организации вызова подпрограмм, включая хранение их
параметров и локально объявленных переменных.
'''
from abc import ABC, abstractmethod
from enum import IntEnum, auto
import numpy as np

from . import traps


class Opcode(IntEnum):
    '''Enumeration of instructions' opcodes
    '''
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
    '''Call frame that stores return address from subprogram (`return_address`)
    and its parameters, and local variables (`variables`).
    '''
    def __init__(self, return_address: np.uint64):
        self.return_address = return_address
        self.variables = {}


class Context:
    '''Context that every instruction operates in. It has:

    + stack of operands - `operands_stack`
    + stack of call frames - `frames`
    + and instruction pointer - `ip` that inits to zero on start
    '''
    def __init__(self):
        self.operands_stack = []
        self.frames = []
        self.ip = np.uint64(0)


def force_uint64(number: int) -> np.uint64:
    '''Converts any int to 64-bit unsigned integer. If integer is out of uint64
    range then cuts off extra bits.

    :param number: integer to convert
    :type number: int

    :return: integer that fits into unsigned integer 64-bit
    :rtype: class:`np.uint64`
    '''
    if number < 0:
        number += (1 << 64)
    if number >= (1 << 64):
        number &= (1 << 64) - 1
    return np.uint64(number)


class Instruction(ABC):
    '''Abstract VM instruction.
    '''
    @classmethod
    @abstractmethod
    def opcode(cls) -> Opcode:
        '''Returns opcode of instruction cause of its type.

        :return: instruction's opcode
        :rtype: class:`Opcode`
        '''
        raise NotImplementedError

    @abstractmethod
    def args(self) -> list[np.uint64]:
        '''Returns instruction's arguments.

        :return: list of instruction's arguments as unsigned 64-bit integers
        :rtype: list[class:`np.uint64`]
        '''
        raise NotImplementedError

    @abstractmethod
    def execute(self, ctx: Context) -> bool:
        '''Instruction's execution routine.

        :param ctx: calculation context
        :type ctx: class:`Context`

        :return: should stop subsequent execution
        :rtype: bool
        '''
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def nargs(cls) -> int:
        '''Returns number of arguments that instruction uses.

        :return: number of arguments
        :rtype: int
        '''
        raise NotImplementedError

    def __repr__(self) -> str:
        '''Returns string representation of the instruction.

        :return: string representation of instruction
        :rtype: str
        '''
        components = [type(self).__name__]
        if self.nargs() > 0:
            components.append('(')
            components.append(', '.join(map(hex, self.args())))
            components.append(')')
        return ''.join(components)


class NoOperation(Instruction):
    '''No operation instruction - does nothing.
    '''
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
    '''Pushes its argument onto the operands stack.
    '''
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
    '''Pops element from the operands stack. Throws
    class:`rusty.traps.StackUnderflowTrap` if there are not enough elements on
    the stack.
    '''
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
    '''Pops two elements from the stack and pushes them back in different order.
    Throws class:`rusty.traps.StackUnderflowTrap` if there are no enough elements.
    '''
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
    '''Pushes onto the operands stack the copy of its top element. Throws
    class:`rusty.traps.StackUnderflowTrap` if operands stack is empty.
    '''
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
    '''Representation of every VM instruction that consumes two operands from
    the stack and pushes some single number back.
    '''
    @abstractmethod
    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        '''Consumes two numbers and produces a single one.

        :param a: first operand
        :type a: class:`np.uint64`
        :param b: second operand
        :type b: class:`np.uint64`

        :return: result of applying f(a, b)
        :rtype: class:`np.uint64`
        '''
        raise NotImplementedError

    def execute(self, ctx: Context) -> bool:
        '''Pops two operands from stack and passes them to callback. And result
        of the callback is pushed on stack back. If the stack contained less than
        2 elements then class:`rusty.traps.StackUnderflowTrap` would be thrown.

        :param self: instruction
        :type self: any subclass of class:`rusty.isa.BinaryApplyInstruction`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after executing this type of
        instructions
        :rtype: bool
        '''
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
    '''Adds 2 numbers from the operands stack and pushes result back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.ADD

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a + b

class Substract(BinaryApplyInstruction):
    '''Substracts 2 numbers from the operands stack and pushes result back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SUB

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a - b

class Multiply(BinaryApplyInstruction):
    '''Multiplies 2 numbers from the operands stack and pushes result back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MUL

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a * b

class Divide(BinaryApplyInstruction):
    '''Divides 2 numbers from the operands stack and pushes result back. If the
    divider was 0 then class:`rusty.traps.ZeroDivisionTrap` would be thrown.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.DIV

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        if b == 0:
            raise traps.ZeroDivisionTrap
        return a / b

class Modulo(BinaryApplyInstruction):
    '''Divides 2 numbers from the operands stack and pushes remainder of the
    division back. If the divider was 0 then class:`rusty.traps.ZeroDivisionTrap`
    would be thrown.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MOD

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        if b == 0:
            raise traps.ZeroDivisionTrap
        return a % b

class ShiftLeft(BinaryApplyInstruction):
    '''Shifts left first operand by second operand positions and pushes result
    back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SHL

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a << b

class ShiftRight(BinaryApplyInstruction):
    '''Shifts right first operand by second operand positions and pushes result
    back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.SHR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a >> b


class Maximum(BinaryApplyInstruction):
    '''Finds maximum between 2 numbers from the operands stack and pushes result
    back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MAX

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a if a > b else b

class Minimum(BinaryApplyInstruction):
    '''Finds minimum between 2 numbers from the operands stack and pushes result
    back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.MIN

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a if a < b else b

class And(BinaryApplyInstruction):
    '''Calculates bitwise AND between 2 numbers from the operands stack and
    pushes result back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.AND

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a & b

class Or(BinaryApplyInstruction):
    '''Calculates bitwise OR between 2 numbers from the operands stack and
    pushes result back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.OR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a | b

class Xor(BinaryApplyInstruction):
    '''Calculates XOR between 2 numbers from the operands stack and pushes result
    back.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.XOR

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return a ^ b


class UnaryApplyInstruction(Instruction):
    '''Represents all unary VM instructions that pops a single number from the
    operands stack and pushes some result back.
    '''
    @abstractmethod
    def _apply(self, a: np.uint64) -> np.uint64:
        '''Consumes single number and produces another one.

        :param a: operand
        :type a: class:`np.uint64`

        :return: result of applying f(a)
        :rtype: class:`np.uint64`
        '''
        raise NotImplementedError

    def execute(self, ctx: Context) -> bool:
        '''Pops single operand from the stack and pushes the result of the
        callback back.

        :param self: instance of unary VM instruction
        :type self: subclass of class:`rusty.isa.UnaryApplyInstruction`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after executing this type of
        instructions
        :rtype: bool
        '''
        try:
            a = ctx.operands_stack.pop()
            ctx.operands_stack.append(self._apply(a))
        except IndexError:
            raise traps.StackUnderflowTrap
        return False

    def args(self) -> list[np.uint64]:
        return []

    @classmethod
    def nargs(cls) -> int:
        return 0

class Increment(UnaryApplyInstruction):
    '''Pops a single number from the operands stack, increments it and pushes
    result back - `a` -> `a + 1`.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.INC

    def _apply(self, a: np.uint64) -> np.uint64:
        return a + 1

class Decrement(UnaryApplyInstruction):
    '''Pops a single number from the operands stack, decrements it and pushes
    result back - `a` -> `a - 1`.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.DEC

    def _apply(self, a: np.uint64) -> np.uint64:
        return a - 1

class Negate(UnaryApplyInstruction):
    '''Pops a single number from the operands stack and pushes its arithmetic
    negation back - `a` -> `-a`.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NEG

    def _apply(self, a: np.uint64) -> np.uint64:
        return -a

class Not(UnaryApplyInstruction):
    '''Pops a single number from the operands stack and pushes its logic
    negation back - `a` -> `~a`.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NOT

    def _apply(self, a: np.uint64) -> np.uint64:
        return ~a


class LessThan(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if first one is strictly
    less than the second or zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LT

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a < b else 0

class LessOrEqual(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if first one is less
    than or equal to the second or zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LE

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a <= b else 0

class Equal(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if they are equal or
    zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.EQ

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a == b else 0

class NotEqual(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if they are not equal
    or zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.NEQ

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a != b else 0

class GreaterThan(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if first one is strictly
    greater than the second or zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.GT

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a > b else 0

class GreaterOrEqual(BinaryApplyInstruction):
    '''Compares two operands from the stack and pushes 1 if first one is greater
    than or equal to the second or zero.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.GE

    def _apply(self, a: np.uint64, b: np.uint64) -> np.uint64:
        return 1 if a >= b else 0


class Load(Instruction):
    '''Pushes onto the operands stack the value of variable with the provided
    identifier. Pushes zero if the variable with such identifier is not exist.
    '''
    def __init__(self, variable_id: int):
        self.variable_id = force_uint64(variable_id)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.LOAD

    def args(self) -> list[np.uint64]:
        return [self.variable_id]

    def execute(self, ctx: Context) -> bool:
        '''Looks up for the variable in the current call frame and pushes its
        value onto the stack. If variable is not exist then zero is pushed.

        :param self: instance of Load instruction
        :type self: class:`rusty.isa.Load`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after execution of the load
        instructions
        :rtype: bool
        '''
        variable_value = ctx.frames[-1].variables.get(self.variable_id, 0)
        ctx.operands_stack.append(variable_value)
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Store(Instruction):
    '''Stores operand from the stack as the new value of variable of the current
    call frame with the provided identifier. If stack is empty throws
    class:`rusty.traps.StackUnderflowTrap`.
    '''
    def __init__(self, variable_id: int):
        self.variable_id = force_uint64(variable_id)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.STORE

    def args(self) -> list[np.uint64]:
        return [self.variable_id]

    def execute(self, ctx: Context) -> bool:
        '''Pops value from the operands stack. Stores it to the current call
        frame as the value of the variable. The variable is identified by the
        numerical identifier that is got from the instruction argument. Throws
        class:`rusty.traps.StackUnderflowTrap` if the operands stack is empty.

        :param self: instance of Store instruction
        :type self: class:`rusty.isa.Store`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after execution of the store
        instructions
        :rtype: bool
        '''
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
    '''Calls a subprogram. Pushes a new frame onto the call frames stack. The
    frame will use the current IP as the return address from the subprogram.
    Jumps to the subprogram address (instruction's argument).
    '''
    def __init__(self, arg: int):
        self.arg = force_uint64(arg)

    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.CALL

    def args(self) -> list[np.uint64]:
        return [self.arg]

    def execute(self, ctx: Context) -> bool:
        '''Calls a subprogram.

        :param self: instance of Call instruction
        :type self: class:`rusty.isa.Call`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after execution of the call
        instructions
        :rtype: bool
        '''
        ctx.frames.append(Frame(ctx.ip))
        ctx.ip = ctx.ip - 1 + self.arg
        return False

    @classmethod
    def nargs(cls) -> int:
        return 1


class Return(Instruction):
    '''Returns from a subprogram. Pops out the top of the call frames stack and
    jumps the specified by the popped frame return address. If call frames stack
    is empty then throws class:`rusty.traps.StackUnderflowTrap`.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.RET

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        '''Returns from a subprogram.

        :param self: instance of Return instruction
        :type self: class:`rusty.isa.Return`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: false - VM should not stop after execution of the return
        instructions
        :rtype: bool
        '''
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
    '''Jumps to the address that is relative to the current IP by the number
    that is encoded in this instruction as argument.
    '''
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
    '''Pops boolean value from the operands stack and jumps to relative to
    the current IP address if and only if popped value is not equal to zero.
    Throws class:`rusty.traps.StackUnderflowTrap` if stack is empty.
    '''
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
    '''Stops the subsequent instructions execution.
    '''
    @classmethod
    def opcode(cls) -> Opcode:
        return Opcode.STOP

    def args(self) -> list[np.uint64]:
        return []

    def execute(self, ctx: Context) -> bool:
        '''Returns from a subprogram.

        :param self: instance of Stop instruction
        :type self: class:`rusty.isa.Stop`
        :param ctx: calculation context
        :type ctx: class:`rusty.isa.Context`

        :return: true - VM should stop after execution of the stop
        instructions
        :rtype: bool
        '''
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
