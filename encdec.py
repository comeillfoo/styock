#!/usr/bin/env python3
import struct
from typing import TypeVar

import isa
import traps


OPCODE_MASK = (1 << 8) - 1
PADDING_MASK = (1 << 56) - 1


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


def decode_single(bytes: bytes) -> isa.Instruction:
    assert len(bytes) == 8
    raw_ins = struct.unpack('<Q', bytes)
    opcode = isa.Opcode((raw_ins >> 56) & OPCODE_MASK)
    arg = raw_ins & PADDING_MASK
    try:
        cls = isa.INSTRUCTIONS_MAP.get(opcode)
        return cls(arg) if cls.nargs() > 0 else cls()
    except KeyError:
        raise traps.IllegalInstructionTrap


def decode_program(bytes: bytes) -> list[isa.Instruction]:
    return list(map(decode_single,
                    [ bytes[0 + i:8 + i] for i in range(0, len(bytes), 8) ]))
