#!/usr/bin/env python3
import unittest
import antlr4
from rustyc.libs.RustyLexer import RustyLexer
from rustyc.libs.RustyParser import RustyParser
from rustyc.frontend import FERListener


def translate(program: str) -> str:
    lexer = RustyLexer(antlr4.InputStream(program))
    parser = RustyParser(antlr4.CommonTokenStream(lexer))
    crate = parser.crate()
    listener = FERListener()
    antlr4.ParseTreeWalker().walk(listener, crate)
    return listener.tree[crate]


class RustycRulesCases(unittest.TestCase):
    INTEGER_SUFFIXES = [ '', 'i8', 'u8', 'i16', 'u16', 'i32', 'u32', 'i64', 'u64',
        'i128', 'u128', 'isize', 'usize' ]

    def test_empty_function(self):
        source_code = translate('fn main() { }')
        self.assertEqual(source_code, '''\tcall main
\tstop
main:

\tret''')


    def test_positive_decimal_literals(self):
        integers = [0, 1, 2, 42, 128, 2**32, 2**64 - 1]
        for integer in integers:
            for suffix in self.INTEGER_SUFFIXES:
                program = 'fn main() { ' + str(integer) + suffix + ' }'
                source_code = translate(program)
                self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {integer}
\tret''')


    def test_negative_decimal_literals(self):
        integers = [-(2**64), -(2**32), -42, -2, -1]
        for integer in integers:
            for suffix in self.INTEGER_SUFFIXES:
                program = 'fn main() { ' + str(integer) + suffix + ' }'
                source_code = translate(program)
                self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {abs(integer)}
\tneg
\tret''')


    def test_hexadecimal_literals(self):
        integers = [0, 1, 2, 42, 128, 2**32, 2**64 - 1]
        for integer in integers:
            for suffix in self.INTEGER_SUFFIXES:
                literal = hex(integer)
                program = 'fn main() { ' + literal + suffix + ' }'
                source_code = translate(program)
                self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {literal}
\tret''')


    def test_octal_literals(self):
        integers = [0, 1, 2, 42, 128, 2**32, 2**64 - 1]
        for integer in integers:
            for suffix in self.INTEGER_SUFFIXES:
                literal = oct(integer)
                program = 'fn main() { ' + literal + suffix + ' }'
                source_code = translate(program)
                self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {literal}
\tret''')


    def test_binary_literals(self):
        integers = [0, 1, 2, 42, 128, 2**32, 2**64 - 1]
        for integer in integers:
            for suffix in self.INTEGER_SUFFIXES:
                literal = bin(integer)
                program = 'fn main() { ' + literal + suffix + ' }'
                source_code = translate(program)
                self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {literal}
\tret''')


    def test_boolean_literals(self):
        booleans = {
            'true': '1',
            'false': '0'
        }
        for boolean, numerical in booleans.items():
            program = 'fn main() { ' + boolean + ' }'
            source_code = translate(program)
            self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {numerical}
\tret''')


    def test_simple_expressions(self):
        binary_operations = {
            '+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod',
            '<<': 'shl', '>>': 'shr', '&': 'and', '|': 'or', '^': 'xor',
            '&&': 'and', '||': 'or', '==': 'eq', '!=': 'neq', '<': 'lt',
            '>': 'gt', '<=': 'le', '>=': 'ge'
        }
        for binop, ins in binary_operations.items():
            arg1 = 42
            arg2 = 86
            program = 'fn main() { %d %s %d }' % (arg1, binop, arg2)
            source_code = translate(program)
            self.assertEqual(source_code, f'''\tcall main
\tstop
main:
\tpush {arg1}
\tpush {arg2}
\t{ins}
\tret''')


if __name__ == '__main__':
    unittest.main()
