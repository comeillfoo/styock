#!/usr/bin/env python3
import sys
import antlr4

from libs.RustyLexer import RustyLexer
from libs.RustyListener import RustyListener
from libs.RustyParser import RustyParser


class RustyPrintListener(RustyListener):
    def enterHi(self, ctx: RustyParser.HiContext):
        print('Hello', ctx.ID())


def main() -> int:
    lexer = RustyLexer(antlr4.StdinStream(encoding='utf-8'))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = RustyParser(token_stream)

    tree = parser.hi()
    printer = RustyPrintListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
