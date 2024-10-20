#!/usr/bin/env python3
from typing import Tuple
import numpy as np


from . import isa


class StackView:
    def __init__(self, stack: list[np.uint64]):
        self._stack = stack

    def __repr__(self) -> str:
        return '\n'.join([ '#' + str(i) + '\t' + hex(elem) for i, elem in enumerate(self._stack) ])


class InstructionView:
    def __init__(self, instruction: isa.Instruction):
        self._instruction = instruction

    def __repr__(self) -> str:
        args = ' '.join(map(hex, self._instruction.args()))
        return self._instruction.opcode().name + ('\t' + args if self._instruction.nargs() > 0 else '')


class Interpreter:
    def __init__(self):
        self.ctx = isa.Context()
        self.program = []
        self.is_halted = True
        self.breakpoints = []
        self.breaklines = set()

    def load_program(self, program: list[isa.Instruction]):
        self.program = program
        self.is_halted = False

    def info_breakpoints(self) -> list[Tuple[int, isa.Instruction]]:
        return [ (line_no, self.program[line_no]) for line_no in self.breakpoints ]

    def _info_stack(self, stack: list[np.uint64]) -> StackView:
        return StackView(stack)

    def info_args(self) -> StackView:
        return self._info_stack(self.ctx.operands_stack)

    def info_rets(self) -> StackView:
        return self._info_stack(self.ctx.reta_stack)

    def ip(self) -> int:
        return self.ctx.ip

    def list_(self, address: int) -> InstructionView:
        if address > len(self.program) or address < 0:
            raise ValueError # TODO: define own exceptions
        return InstructionView(self.program[address])

    def current_instruction(self) -> InstructionView:
        return self.list(self.ip())

    def is_encountered_breakpoint(self) -> bool:
        return self.ctx.ip in self.breaklines

    def next(self, times: int = 1):
        if self.is_halted:
            return
        for _ in range(times):
            self.ctx.ip += 1
            self.is_halted = self.program[self.ctx.ip - 1].execute(self.ctx)

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
