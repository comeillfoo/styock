#!/usr/bin/env python3
'''Модуль, инкапсулирующий кодирование и декодирование инструкций к ВМ из
текстового в бинарный формат и наоборот.
'''
import struct
from typing import TypeVar

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
    '''Returns list element at index if exist or default value.

    :param lst: list under search
    :type lst: list[T]
    :param i: index of element in list to return
    :type i: int
    :param default:

    :return: element at list or default if no such index
    :rtype: T - the same as the list's elements
    '''
    try:
        return lst[i]
    except IndexError:
        return default


def encode_single(instruction: isa.Instruction) -> bytes:
    '''Encodes single VM instruction object to sequence of bytes.

    :param instruction: single VM instruction
    :type instruction: class:`rusty.isa.Instruction`

    :return: array of bytes
    :rtype: bytes
    '''
    arg = _iordefault(instruction.args(), 0, 0) & PADDING_MASK
    opcode = ((instruction.opcode() & OPCODE_MASK) << 56)
    return struct.pack('<Q', opcode | arg)


def encode_program(instructions: list[isa.Instruction]) -> bytes:
    '''Encodes list of VM instructions to sequence of bytes

    :param instructions: list of VM instructions
    :type instructions: list[class:`rusty.isa.Instruction`]

    :return: array of bytes
    :rtype: bytes
    '''
    return b''.join(map(encode_single, instructions))


def parse_program(lines: list[str]) -> list[isa.Instruction]:
    '''Parses textual program into list of VM instructions

    :param lines: list of textual VM instructions
    :type lines: list[str]

    :return: list of VM instructions
    :rtype: list[class:`rusty.isa.Instruction`]
    '''
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
    '''Decodes 8 bytes to VM instruction.

    :param bytes: 8 bytes
    :type bytes: bytes

    :return: VM instruction
    :rtype: class:`rusty.isa.Instruction`
    '''
    assert len(bytes) == 8
    raw_ins = struct.unpack('<Q', bytes)[0]
    opcode = isa.Opcode((raw_ins >> 56) & OPCODE_MASK)
    arg = raw_ins & PADDING_MASK
    if arg & ((PADDING_MASK + 1) >> 1):
        arg |= ~PADDING_MASK
    try:
        cls = isa.INSTRUCTIONS_MAP.get(opcode)
        return cls(isa.force_uint64(arg)) if cls.nargs() > 0 else cls()
    except KeyError:
        raise traps.IllegalInstructionTrap


def decode_program(bytes: bytes) -> list[isa.Instruction]:
    '''Decodes bytes-sequence into list of VM instructions.

    :param bytes: bytes-sequence
    :type bytes: bytes

    :return: list of VM instructions
    :rtype: list[class:`rusty.isa.Instruction`]
    '''
    return list(map(decode_single,
                    [ bytes[0 + i:8 + i] for i in range(0, len(bytes), 8) ]))
