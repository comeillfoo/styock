#!/usr/bin/env python3
import struct
from typing import TypeVar
import numpy as np

import vm.ISA as ISA
import vm.Traps as Traps


OPCODE_MASK = (1 << 8) - 1
PADDING_MASK = (1 << 56) - 1


ListElement = TypeVar('ListElement')

def _iordefault(lst: list[ListElement], i: int, default: ListElement) -> ListElement:
    try:
        return lst[i]
    except IndexError:
        return default


def encode_single(instruction: ISA.Instruction) -> bytes:
    arg = _iordefault(instruction.args(), 0, 0) & PADDING_MASK
    opcode = ((instruction.opcode() & OPCODE_MASK) << 56)
    return struct.pack('<Q', opcode | arg)


def encode_program(instructions: list[ISA.Instruction]) -> bytes:
    return b''.join(map(encode_single, instructions))


def decode_single(bytes: bytes) -> ISA.Instruction:
    assert len(bytes) == 8
    raw_ins = struct.unpack('<Q', bytes)
    opcode = ISA.Opcode((raw_ins >> 56) & OPCODE_MASK)
    arg = raw_ins & PADDING_MASK
    try:
        cls = ISA.INSTRUCTIONS_MAP.get(opcode)
        return cls(np.uint64(arg)) if cls.nargs() > 0 else cls()
    except KeyError:
        raise Traps.IllegalInstructionTrap


def decode_program(bytes: bytes) -> list[ISA.Instruction]:
    return list(map(decode_single,
                    [ bytes[0 + i:8 + i] for i in range(0, len(bytes), 8) ]))
