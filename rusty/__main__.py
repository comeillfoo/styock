#!/usr/bin/env python3
'''Главный модуль, реализующий утилиту с командами по переводу инструкций к
стековой виртуальной машине из текстового формата в бинарный и обратно. А также
с командой исполнения программы из бинарного файла с инструкциями к ВМ.'''
import os
import errno
import sys
import argparse
import pathlib
import pprint

from .vm import VM
from .decenc import encode_program, parse_program, decode_program


def run(args: argparse.Namespace) -> int:
    '''Reads instructions from binary file and executes them.

    :param args: command-line arguments
    :type args: class:`argparse.Namespace`

    :return: error code, zero on success
    :rtype: int
    '''
    if not os.path.isfile(args.bytecode):
        print('File', args.bytecode, 'not found')
        return errno.ENOENT

    with open(args.bytecode, 'rb') as fp:
        program = decode_program(fp.read())

    vm = VM(args.verbose)
    vm.load_program(program)
    try:
        vm.run()
    finally:
        print(vm.info_operands())
        print(vm.info_frames())
    return 0


def encode(args: argparse.Namespace) -> int:
    '''Encodes textual list of instructions to binary file.

    :param args: command-line arguments
    :type args: class:`argparse.Namespace`

    :return: error code, zero on success
    :rtype: int
    '''
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
    '''Decodes binary file with VM instructions to textual list of objects.

    :param args: command-line arguments
    :type args: class:`argparse.Namespace`

    :return: error code, zero on success
    :rtype: int
    '''
    if not os.path.isfile(args.bytecode):
        print('File', args.bytecode, 'not found')
        return errno.ENOENT

    with open(args.bytecode, mode='rb') as fp:
        pprint.pprint(decode_program(fp.read()))


def args_parser() -> argparse.ArgumentParser:
    '''Builds arguments parser with commands: `run`, `encode` and decode.

    :return: arguments parser
    :rtype: class:`argparse.ArgumentParser`
    '''
    p = argparse.ArgumentParser('rusty')
    subp = p.add_subparsers(title='subcommands')

    runner_p = subp.add_parser('run', help='runs bytecode')
    runner_p.add_argument('bytecode', type=pathlib.Path, metavar='PATH',
                          help='path to bytecode in binary format')
    runner_p.add_argument('--verbose', '-v', action='store_true',
                          help='print ip and instruction on execution')
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
    '''Main routine that parses command-line arguments and runs corresponding
    command.

    :return: error code, zero on success
    :rtype: int
    '''
    args = args_parser().parse_args()
    return args.func(args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!', file=sys.stderr)
        sys.exit(1)
