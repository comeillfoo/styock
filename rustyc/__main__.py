#!/usr/bin/env python3
'''Главный модуль пакета компилятора языка Rusty (),
транслирующего подмножество языка Rust в инструкции стековой виртуальной машины
в виде текста.
'''
import os
import sys
import errno
import argparse
import pathlib
import antlr4

from .libs.RustyLexer import RustyLexer
from .libs.RustyParser import RustyParser

from .frontend import FERListener
from .backend import process


def args_parser() -> argparse.ArgumentParser:
    '''Builds arguments parser that supports options for redirecting output to
    specific file, enumerating every instruction for debugging and so on.

    :return: arguments parser
    :rtype: class:`argparse.ArgumentParser`
    '''
    p = argparse.ArgumentParser('rustyc')

    # Options:
    p.add_argument('--output', '-o', type=pathlib.Path, metavar='PATH',
                   help='Path to output file, default stdout')
    p.add_argument('--only-frontend', '-f', action='store_true',
                   help='Exclude backend-stage, only frontend')
    p.add_argument('--ip', '-i', action='store_true',
                   help='Prepend instruction pointer value for current instruction at backend')

    # Arguments:
    p.add_argument('file', type=pathlib.Path, help='Path to source file')
    return p


def main() -> int:
    '''Main routine that implements compiler that parses input subrust program
    (taken from the argument) and translates it into textual stack-based VM
    instructions.

    :return: error code - zero on success
    :rtype: int
    '''
    args = args_parser().parse_args()
    if not os.path.isfile(args.file):
        print('File', args.file, 'not found', file=sys.stderr)
        return errno.ENOENT

    out = sys.stdout
    if args.output is not None:
        out = open(args.output, 'w', encoding='utf-8')

    lexer = RustyLexer(antlr4.FileStream(args.file, encoding='utf-8'))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = RustyParser(token_stream)

    root_crate = parser.crate()
    listener = FERListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, root_crate)

    source_code = listener.tree[root_crate]
    if not args.only_frontend:
        source_code = process(source_code, should_prepend=args.ip)
    print(source_code, file=out)
    out.close()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
