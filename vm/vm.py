#!/usr/bin/env python3
import sys
import argparse
import pathlib

import vm.ISA as ISA
import vm.Traps as Traps
from vm.Interpreter import Interpreter


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()

    p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                   help='Path to program in bytecode program')
    return p


def main() -> int:
    program: list[ISA.Instruction] = [
        ISA.Push(10),
        ISA.Push(20),
        ISA.Add(),
        ISA.Call(1),
        ISA.Stop(),
        ISA.Push(40),
        ISA.Add(),
        ISA.Ret()
    ]
    vm = Interpreter()
    vm.load_program(program)
    try:
        vm.run()
    except IndexError:
        raise Traps.InvalidAddressTrap

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
