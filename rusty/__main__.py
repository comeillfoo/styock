#!/usr/bin/env python3
import os
import errno
import sys
import argparse
import pathlib

from . import ISA, Traps
from .Interpreter import Interpreter
from .EncDec import encode_program, parse_program, decode_program


def run(args: argparse.Namespace) -> int:
    program: list[ISA.Instruction] = [
        ISA.Push(10),
        ISA.Push(20),
        ISA.Add(),
        ISA.Call(1),
        ISA.Stop(),
        ISA.Push(40),
        ISA.Add(),
        ISA.Return()
    ]
    vm = Interpreter()
    vm.load_program(program)
    try:
        vm.run()
    except IndexError:
        raise Traps.InvalidAddressTrap
    return 0


def encode(args: argparse.Namespace) -> int:
    if not os.path.isfile(args.bytecode):
        print('File', args.bytecode, 'not found')
        return errno.ENOENT

    instructions = []
    with open(args.bytecode, encoding='utf-8') as fp:
        instructions.extend(parse_program(fp.readlines()))
    print(instructions)
    print(encode_program(instructions))



def decode(args: argparse.Namespace) -> int:
    if not os.path.isfile(args.bytecode):
        print('File', args.bytecode, 'not found')
        return errno.ENOENT

    with open(args.bytecode, mode='rb') as fp:
        print(decode_program(fp.read()))


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser('rusty')
    subp = p.add_subparsers(title='subcommands')

    runner_p = subp.add_parser('run', help='runs bytecode')
    runner_p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                          help='path to bytecode in binary format')
    runner_p.set_defaults(func=run)

    encoder_p = subp.add_parser('encode', help='translates bytecode from text to binary')
    encoder_p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                           help='path to bytecode in text format')
    encoder_p.add_argument('--output', '-o', type=pathlib.Path, metavar='OUT',
                           help='where to save resulting binary')
    encoder_p.set_defaults(func=encode)

    decoder_p = subp.add_parser('decode', help='translates bytecode from binary to text')
    decoder_p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                           help='path to bytecode in binary format')
    decoder_p.add_argument('--output', '-o', type=pathlib.Path, metavar='OUT',
                           help='where to save resulting source code')
    decoder_p.set_defaults(func=decode)

    return p


def main() -> int:
    args = args_parser().parse_args()
    return args.func(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
