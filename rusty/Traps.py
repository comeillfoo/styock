#!/usr/bin/env python3
class Trap(Exception):
    pass


class StackUnderflowTrap(Trap):
    pass


class InvalidAddressTrap(Trap):
    pass


class IllegalInstructionTrap(Trap):
    pass

class ZeroDivisionTrap(Trap):
    pass
