#!/usr/bin/env python3
import sys
import argparse
import pathlib


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()

    p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                   help='Path to program in bytecode program')
    return p


def main() -> int:
    args = args_parser().parse_args()
    with open(args.bytecode, mode='rb') as fp:
        pass
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
