#!/usr/bin/env python3
import os
import errno
import sys
import argparse
import pathlib
import pprint

from . import isa, traps
from .interpreter import Interpreter
from .decenc import encode_program, parse_program, decode_program


def run(args: argparse.Namespace) -> int:
    program: list[isa.Instruction] = [
        isa.Push(10),
        isa.Push(20),
        isa.Add(),
        isa.Call(1),
        isa.Stop(),
        isa.Push(40),
        isa.Add(),
        isa.Return()
    ]
    vm = Interpreter()
    vm.load_program(program)
    try:
        vm.run()
    except IndexError:
        raise traps.InvalidAddressTrap
    return 0


def encode(args: argparse.Namespace) -> int:
    if not os.path.isfile(args.source):
        print('File', args.source, 'not found')
        return errno.ENOENT

    instructions = []
    with open(args.source, encoding='utf-8') as fp:
        instructions.extend(parse_program(fp.readlines()))
    if args.print_parse:
        pprint.pprint(instructions)
        return 0

    with open(args.destination, 'wb') as fp:
        fp.write(encode_program(instructions))
    return 0



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

    encoder_p = subp.add_parser('encode', help='translates source from text to binary')
    encoder_p.add_argument('source', type=pathlib.Path, metavar='SOURCE',
                           help='path to source in text format')
    encoder_p.add_argument('destination', type=pathlib.Path, metavar='DEST',
                           help='where to save resulting binary')
    encoder_p.add_argument('--print-parse', '-p', action='store_true',
                           help='skips encoding, only prints parsed instructions')
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
