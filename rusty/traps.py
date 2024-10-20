#!/usr/bin/env python3
class Trap(Exception):
    pass


class StackUnderflowTrap(Trap):
    pass


class InvalidAddressTrap(Trap):
    def __init__(self, address: int):
        super().__init__(f'invalid address[{hex(address)}] accessed')


class IllegalInstructionTrap(Trap):
    pass


class ZeroDivisionTrap(Trap):
    pass
