#!/usr/bin/env python3
import struct
from typing import TypeVar
import numpy as np

from . import isa
from . import traps


OPCODE_MASK = (1 << 8) - 1
PADDING_MASK = (1 << 56) - 1

INSTRUCTIONS_NAMES = {
    'nop':   isa.Opcode.NOP,
    'push':  isa.Opcode.PUSH,
    'pop':   isa.Opcode.POP,
    'swap':  isa.Opcode.SWAP,
    'dup':   isa.Opcode.DUP,
    'add':   isa.Opcode.ADD,
    'sub':   isa.Opcode.SUB,
    'mul':   isa.Opcode.MUL,
    'div':   isa.Opcode.DIV,
    'mod':   isa.Opcode.MOD,
    'shl':   isa.Opcode.SHL,
    'shr':   isa.Opcode.SHR,
    'max':   isa.Opcode.MAX,
    'min':   isa.Opcode.MIN,
    'and':   isa.Opcode.AND,
    'or':    isa.Opcode.OR,
    'xor':   isa.Opcode.XOR,
    'inc':   isa.Opcode.INC,
    'dec':   isa.Opcode.DEC,
    'neg':   isa.Opcode.NEG,
    'not':   isa.Opcode.NOT,
    'lt':    isa.Opcode.LT,
    'le':    isa.Opcode.LE,
    'eq':    isa.Opcode.EQ,
    'neq':   isa.Opcode.NEQ,
    'ge':    isa.Opcode.GE,
    'gt':    isa.Opcode.GT,
    'load':  isa.Opcode.LOAD,
    'store': isa.Opcode.STORE,
    'call':  isa.Opcode.CALL,
    'ret':   isa.Opcode.RET,
    'jmp':   isa.Opcode.JMP,
    'jift':  isa.Opcode.JIFT,
    'stop':  isa.Opcode.STOP,
}


ListElement = TypeVar('ListElement')

def _iordefault(lst: list[ListElement], i: int, default: ListElement) -> ListElement:
    try:
        return lst[i]
    except IndexError:
        return default


def encode_single(instruction: isa.Instruction) -> bytes:
    arg = _iordefault(instruction.args(), 0, 0) & PADDING_MASK
    opcode = ((instruction.opcode() & OPCODE_MASK) << 56)
    return struct.pack('<Q', opcode | arg)


def encode_program(instructions: list[isa.Instruction]) -> bytes:
    return b''.join(map(encode_single, instructions))


def parse_program(lines: list[str]) -> list[isa.Instruction]:
    instructions = []
    for line in lines:
        parts = line.strip().split(' ', 1)
        raw_instruction = parts[0]
        opcode = INSTRUCTIONS_NAMES.get(raw_instruction, None)
        if opcode is None:
            raise Exception # unknown instruction encountered
        cls = isa.INSTRUCTIONS_MAP.get(opcode, None)
        if cls is None:
            raise Exception # unknown opcode encountered

        if cls.nargs() > 0:
            args = list(map(int, parts[1:]))
            instructions.append(cls(*args))
            continue
        instructions.append(cls())

    return instructions


def decode_single(bytes: bytes) -> isa.Instruction:
    assert len(bytes) == 8
    raw_ins = struct.unpack('<Q', bytes)[0]
    opcode = isa.Opcode((raw_ins >> 56) & OPCODE_MASK)
    arg = raw_ins & PADDING_MASK
    try:
        cls = isa.INSTRUCTIONS_MAP.get(opcode)
        return cls(np.uint64(arg)) if cls.nargs() > 0 else cls()
    except KeyError:
        raise traps.IllegalInstructionTrap


def decode_program(bytes: bytes) -> list[isa.Instruction]:
    return list(map(decode_single,
                    [ bytes[0 + i:8 + i] for i in range(0, len(bytes), 8) ]))
