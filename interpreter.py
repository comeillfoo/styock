#!/usr/bin/env python3
from typing import Tuple
import numpy as np


import isa


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

    def _info_stack(self, stack: list[np.uint64]) -> list:
        pass

    def info_args(self) -> list:
        return self._info_stack(self.ctx.args_stack)

    def info_rets(self):
        return self._info_stack(self.ctx.reta_stack)

    def is_encountered_breakpoint(self) -> bool:
        return self.ctx.ip in self.breaklines

    def next(self):
        self.ctx.ip += 1
        self.is_halted = self.program[self.ctx.ip - 1].execute(self.ctx)

    def _continue(self):
        while not self.is_halted:
            self.next()
            if self.is_encountered_breakpoint():
                break

    def run(self):
        self._continue()

    def break_on(self, line_no: int) -> int:
        if line_no < 0 or line_no >= len(self.program):
            return -1
        self.breakpoints.append(line_no)
        self.breaklines.add(line_no)
        return len(self.breakpoints) - 1

    def delete_bp(self, breakpoint: int):
        line_no = self.breakpoints.pop(breakpoint)
        self.breaklines.remove(line_no)
