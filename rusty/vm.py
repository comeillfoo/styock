#!/usr/bin/env python3
'''Стековая виртуальная машина и все, что с ней связано.
'''
from typing import Tuple
import numpy as np


from . import isa
from . import traps


class OperandView:
    '''Auxilary class for simplifying representation of operands in interactive
    mode.
    '''
    def __init__(self, operand: np.uint64):
        self._operand = operand

    def __repr__(self) -> str:
        return hex(self._operand)


class FrameView:
    '''Auxilary class for simplifying representation of call frame in interactive
    mode.
    '''
    def __init__(self, frame: isa.Frame):
        self._frame = frame

    def __repr__(self) -> str:
        vars = ', '.join(map(lambda k, v: f'{k}: {hex(v)}', self._frame.variables.items()))
        return 'retaddr: ' + hex(self._frame.return_address) + '; vars: ' + '{' + vars + '}'


class StackView:
    '''Auxilary class for simplifying representation of any type of stack in
    interactive mode.
    '''
    def __init__(self, stack: list):
        self._stack = stack

    def __repr__(self) -> str:
        return '\n'.join([ '#' + str(i) + '\t' + elem.__repr__() for i, elem in enumerate(self._stack) ])


class VM:
    '''Stack-based virtual machine that is able to:

    1. load programs from the list of instructions
    2. provide its state
    3. manage breakpoints
    4. control the execution of the instructions (execute single, or until stop)
    '''
    def __init__(self, debug: bool = False):
        self.ctx = None
        self.program = []
        self.is_halted = True
        self.breakpoints = []
        self.breaklines = set()
        self.debug = debug

    def load_program(self, program: list[isa.Instruction]):
        '''Stores list of instructions as the current program of the VM.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :param program: list of VM instructions
        :type program: list[class:`rusty.isa.Instruction`]
        '''
        self.program = program
        self.is_halted = False
        self.ctx = isa.Context()

    def info_breakpoints(self) -> list[Tuple[int, isa.Instruction]]:
        '''Lists created breakpoints.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: list of breakpoints - tuples of instruction's index and the
        instruction itself
        :rtype: list[(int, class:`rusty.isa.Instruction`)]
        '''
        return [ (line_no, self.program[line_no]) for line_no in self.breakpoints ]

    def info_operands(self) -> StackView:
        '''Views stack of operands

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: view of operands stack
        :rtype: class:`rusty.vm.StackView`
        '''
        return StackView(list(map(OperandView, self.ctx.operands_stack)))

    def info_frames(self) -> StackView:
        '''Views stack of call frames

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: view of call frames stack
        :rtype: class:`rusty.vm.StackView`
        '''
        return StackView(list(map(FrameView, self.ctx.frames)))

    def ip(self) -> np.uint64:
        '''Returns current IP (instruction pointer) value.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: IP value
        :rtype: class:`np.uint64`
        '''
        return self.ctx.ip

    def list_(self, address: int) -> isa.Instruction:
        '''Returns instruction at specified address in program.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :param address: index of instruction in list of instructions (program)
        :type address: int

        :return: instruction at address
        :rtype: class:`rusty.isa.Instruction`
        '''
        if address >= len(self.program) or address < 0:
            raise ValueError # TODO: define own exceptions
        return self.program[address]

    def list_range(self, begin: int, end: int) -> list[isa.Instruction]:
        '''Returns instructions at specified address range [begin; end) in program.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :param begin: the begin address in range
        :type begin: int
        :param end: the last address in range
        :type end: int

        :return: instructions at addresses [begin; end)
        :rtype: list[class:`rusty.isa.Instruction`]
        '''
        return [ self.list_(addr) for addr in range(begin, end) ]

    def size(self) -> int:
        '''Number of instructions in loaded program

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: length of the list of instructions of loaded program
        :rtype: int
        '''
        return len(self.program)

    def current_instruction(self) -> isa.Instruction:
        '''Returns current instruction which IP is pointing at.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :return: current instruction
        :rtype: class:`rusty.isa.Instruction`
        '''
        return self.list_(self.ip())

    def is_encountered_breakpoint(self) -> bool:
        '''Tests if IP reaches any breakpoint.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`

        :return: is current IP value points to instruction with the breakpoint
        :rtype: bool
        '''
        return self.ctx.ip in self.breaklines

    def next(self, times: int = 1):
        '''Executes next N instructions.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :param times: number of instructions to execute
        :type times: int, default 1
        '''
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
        '''Continues program execution till the stop instruction or any
        breakpoint.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        '''
        while not self.is_halted:
            self.next()
            if self.is_encountered_breakpoint():
                break

    def run(self):
        '''Runs program from memory till the stop instruction or any breakpoint

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        '''
        self.continue_()

    def break_on(self, line_no: int) -> int:
        '''Creates breakpoint specified program's line.

        :param self: instance of VM
        :type self: class:`rusty.vm.VM`
        :param line_no: index of instruction to stop program execution
        :type line_no: int

        :return: identifier of the created breakpoint
        :rtype: int
        '''
        if line_no < 0 or line_no >= len(self.program):
            return -1
        self.breakpoints.append(line_no)
        self.breaklines.add(line_no)
        return len(self.breakpoints) - 1

    def delete_bp(self, breakpoint: int):
        '''Deletes breakpoint.

        :param breakpoint: identifier of the breakpoint to delete
        :type breakpoint: int
        '''
        line_no = self.breakpoints.pop(breakpoint)
        self.breaklines.remove(line_no)
