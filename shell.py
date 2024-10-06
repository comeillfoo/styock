#!/usr/bin/env python3
import sys
import argparse
import pathlib

import isa
import traps
from interpreter import Interpreter


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()

    p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                   help='Path to program in bytecode program')
    return p


def main() -> int:
    program: list[isa.Instruction] = [
        isa.Push(10),
        isa.Push(20),
        isa.Add(),
        isa.Call(1),
        isa.Stop(),
        isa.Push(40),
        isa.Add(),
        isa.Ret()
    ]
    vm = Interpreter()
    vm.load_program(program)
    try:
        vm.run()
    except IndexError:
        raise traps.InvalidAddressTrap

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
