#!/usr/bin/env python3
from typing import Tuple
import numpy as np


from . import isa
from . import traps


class OperandView:
    def __init__(self, operand: np.uint64):
        self._operand = operand

    def __repr__(self) -> str:
        return hex(self._operand)


class FrameView:
    def __init__(self, frame: isa.Frame):
        self._frame = frame

    def __repr__(self) -> str:
        vars = ', '.join(map(lambda k, v: f'{k}: {hex(v)}', self._frame.variables.items()))
        return 'retaddr: ' + hex(self._frame.return_address) + '; vars: ' + '{' + vars + '}'


class StackView:
    def __init__(self, stack: list):
        self._stack = stack

    def __repr__(self) -> str:
        return '\n'.join([ '#' + str(i) + '\t' + elem.__repr__() for i, elem in enumerate(self._stack) ])


class VM:
    def __init__(self, debug: bool = False):
        self.ctx = isa.Context()
        self.program = []
        self.is_halted = True
        self.breakpoints = []
        self.breaklines = set()
        self.debug = debug

    def load_program(self, program: list[isa.Instruction]):
        self.program = program
        self.is_halted = False

    def info_breakpoints(self) -> list[Tuple[int, isa.Instruction]]:
        return [ (line_no, self.program[line_no]) for line_no in self.breakpoints ]

    def info_operands(self) -> StackView:
        return StackView(list(map(OperandView, self.ctx.operands_stack)))

    def info_frames(self) -> StackView:
        return StackView(list(map(FrameView, self.ctx.frames)))

    def ip(self) -> int:
        return self.ctx.ip

    def list_(self, address: int) -> isa.Instruction:
        if address > len(self.program) or address < 0:
            raise ValueError # TODO: define own exceptions
        return self.program[address]

    def list_range(self, begin: int, end: int) -> list[isa.Instruction]:
        return [ self.list_(addr) for addr in range(begin, end) ]

    def current_instruction(self) -> isa.Instruction:
        return self.list(self.ip())

    def is_encountered_breakpoint(self) -> bool:
        return self.ctx.ip in self.breaklines

    def next(self, times: int = 1):
        if self.is_halted:
            return
        for _ in range(times):
            if self.ctx.ip < 0 or self.ctx.ip >= len(self.program):
                raise traps.InvalidAddressTrap(self.ctx.ip)
            self.ctx.ip += 1
            instruction = self.program[self.ctx.ip - 1]
            if self.debug:
                print(f'{(self.ctx.ip - 1):016x}:', instruction, sep='\t')
            self.is_halted = instruction.execute(self.ctx)

    def continue_(self):
        while not self.is_halted:
            self.next()
            if self.is_encountered_breakpoint():
                break

    def run(self):
        self.continue_()

    def break_on(self, line_no: int) -> int:
        if line_no < 0 or line_no >= len(self.program):
            return -1
        self.breakpoints.append(line_no)
        self.breaklines.add(line_no)
        return len(self.breakpoints) - 1

    def delete_bp(self, breakpoint: int):
        line_no = self.breakpoints.pop(breakpoint)
        self.breaklines.remove(line_no)
