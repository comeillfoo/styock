#!/usr/bin/env python3
import sys
import argparse
import pathlib

import isa


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()

    p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                   help='Path to program in bytecode program')
    return p


def main() -> int:
    program: list[isa.Instruction] = [
        isa.Push(10),
        isa.Push(20),
        isa.Pop(),
        isa.Pop(),
        isa.Stop()
    ]
    ctx = isa.Context()
    should_stop = False
    while not should_stop:
        ctx.ip += 1
        should_stop = program[ctx.ip].execute(ctx)

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
