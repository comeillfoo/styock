#!/usr/bin/env python3
import sys
import argparse
import pathlib

import isa
import traps


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
        isa.Swap(),
        isa.Push(40),
        isa.Add(),
        isa.Swap(),
        isa.Ret()
    ]
    ctx = isa.Context()
    try:
        should_stop = False
        while not should_stop:
            ctx.ip += 1
            print('ip =', ctx.ip - 1, 'stack:', ctx.stack)
            should_stop = program[ctx.ip - 1].execute(ctx)
    except IndexError:
        raise traps.InvalidAddressTrap

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
