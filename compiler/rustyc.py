#!/usr/bin/env python3
import sys
import argparse
import pathlib
import antlr4

from libs.RustyLexer import RustyLexer
from libs.RustyListener import RustyListener
from libs.RustyParser import RustyParser


class RustyListenerImpl(RustyListener):
    pass


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser('rustyc')
    p.add_argument('file', type=pathlib.Path, help='Path to source file')
    return p


def main() -> int:
    args = args_parser().parse_args()
    lexer = RustyLexer(antlr4.FileStream(args.file, encoding='utf-8'))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = RustyParser(token_stream)

    tree = parser.crate()
    listener = RustyListenerImpl()
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, tree)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
