#!/usr/bin/env python3
import os
import sys
import errno
import argparse
import pathlib
import antlr4

from libs.RustyLexer import RustyLexer
from libs.RustyParser import RustyParser

from frontend import FERListener, finstr


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser('rustyc')

    # Options:
    p.add_argument('--output', '-o', type=pathlib.Path, metavar='PATH',
                   help='Path to output file, default stdout')
    p.add_argument('--only-frontend', '-f', action='store_true',
                   help='Exclude backend-stage, only frontend')

    # Arguments:
    p.add_argument('file', type=pathlib.Path, help='Path to source file')
    return p


def main() -> int:
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

    executable = listener.tree[root_crate]
    if not args.only_frontend:
        # TODO: resolve labels and replace jmps and calls
        executable = executable
    print(executable, file=out)
    out.close()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
