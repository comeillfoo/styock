#!/usr/bin/env python3
import unittest
import antlr4
from rustyc.libs.RustyLexer import RustyLexer
from rustyc.libs.RustyParser import RustyParser
from rustyc.frontend import FERListener


class RustycRulesCases(unittest.TestCase):
    def test_empty_function(self):
        lexer = RustyLexer(antlr4.InputStream('fn main() { }'))
        parser = RustyParser(antlr4.CommonTokenStream(lexer))
        listener = FERListener()
        crate = parser.crate()
        antlr4.ParseTreeWalker().walk(listener, crate)
        source_code = listener.tree[crate]
        self.assertEqual(source_code, '''\tcall main
\tstop
main:

\tret''')


if __name__ == '__main__':
    unittest.main()
