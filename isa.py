#!/usr/bin/env python3
from abc import ABC, abstractmethod

import traps


class Context:
    def __init__(self):
        self.stack = []
        self.acc = 0
        self.ip = -1


class Instruction(ABC):
    @abstractmethod
    def execute(self, ctx: Context) -> bool:
        raise NotImplementedError


class Push(Instruction):
    def __init__(self, arg: int):
        self.arg = arg

    def execute(self, ctx: Context) -> bool:
        ctx.stack.append(self.arg)


class Pop(Instruction):
    def __init__(self):
        pass

    def execute(self, ctx: Context) -> bool:
        try:
            ctx.acc = ctx.stack.pop()
            return False
        except IndexError:
            raise traps.StackOverflowTrap


class Stop(Instruction):
    def __init__(self):
        pass

    def execute(self, ctx: Context) -> bool:
        return True

