#!/usr/bin/env python3
import unittest
import numpy as np

from rusty.decenc import encode_program, decode_program
from rusty import isa, traps
from rusty.vm import VM


TEST_PROGRAMS = [
    [isa.Stop()],
    [isa.Push(24), isa.Stop()],
    [isa.Call(1), isa.Return(), isa.Stop()],
    [isa.Push(6), isa.Push(8), isa.Add(), isa.Stop()]
]


class VMUtilitiesCases(unittest.TestCase):
    def test_positives_force_uint64(self):
        for arg in (0, 1, 2, 7, 11, 13, 2**16, 2**32, 2**64 - 1):
            integer = isa.force_uint64(arg)
            self.assertEqual(integer, arg)

    def test_negatives_force_uint64(self):
        for arg in (-2**63, -(2**32), -(2**16 - 1), -13, -11, -7, -2, -1):
            integer = int(isa.force_uint64(arg).view(np.int64))
            self.assertEqual(integer, arg)


class RustyEncodingDecodingCases(unittest.TestCase):
    def test_encode_decode(self):
        for program in TEST_PROGRAMS:
            encoded_program = encode_program(program)
            decoded_program = decode_program(encoded_program)
            self.assertEqual(program, decoded_program)


class RustyVMCases(unittest.TestCase):
    def test_simplest_program(self):
        program = [isa.Stop()]
        vm = VM()
        vm.load_program(program)
        vm.run()
        self.assertTrue(vm.is_halted)

    def test_list(self):
        program = [isa.Stop() for _ in range(256)]
        vm = VM()
        vm.load_program(program)
        for i in range(256):
            self.assertEqual(vm.list_(i), vm.program[i])

    def test_list_out_of_range(self):
        program = [isa.Stop()]
        vm = VM()
        vm.load_program(program)
        for address in (-2, -1, 1, 3, 5, 42):
            with self.assertRaises(ValueError):
                vm.list_(address)

    def test_size(self):
        vm = VM()
        for program in TEST_PROGRAMS:
            vm.load_program(program)
            self.assertEqual(vm.size(), len(program))


class VMInstructionsCases(unittest.TestCase):
    def test_push(self):
        vm = VM()
        for arg in (8, 10, -1, -2, 2**32, 2**63 - 1):
            program = [isa.Push(arg)]
            vm.load_program(program)
            vm.next()
            self.assertEqual(int(vm.ctx.operands_stack[0].view(np.int64)), arg)

    def test_pop(self):
        vm = VM()
        program = [isa.Pop()]
        vm.load_program(program)
        vm.ctx.operands_stack.append(42)
        vm.next()
        self.assertEqual(len(vm.ctx.operands_stack), 0)

        vm.load_program(program)
        with self.assertRaises(traps.StackUnderflowTrap):
            vm.next()

    def test_swap(self):
        vm = VM()
        program = [isa.Swap()]
        vm.load_program(program)
        vm.ctx.operands_stack.extend([1, 2])
        vm.next()
        self.assertEqual(vm.ctx.operands_stack, [2, 1])

        vm.load_program(program)
        with self.assertRaises(traps.StackUnderflowTrap):
            vm.next()

    def test_dup(self):
        vm = VM()
        program = [isa.Duplicate()]
        vm.load_program(program)
        vm.ctx.operands_stack.append(42)
        vm.next()
        self.assertEqual(vm.ctx.operands_stack, [42, 42])

        vm.load_program(program)
        with self.assertRaises(traps.StackUnderflowTrap):
            vm.next()

    def _subtest_binop(self, ins_type, f):
        vm = VM()
        program = [ins_type()]
        for a in (0, 1, 2, 8, 16, 32, 64, 128):
            for b in (0, 1, 2, 7, 15, 31, 63, 127):
                vm.load_program(program)
                vm.ctx.operands_stack.extend([a, b])
                vm.next()
                self.assertEqual(vm.ctx.operands_stack[0], f(a, b))

    def test_add(self):
        self._subtest_binop(isa.Add, lambda a, b: a + b)

    def test_mul(self):
        self._subtest_binop(isa.Multiply, lambda a, b: a * b)

    def test_max(self):
        self._subtest_binop(isa.Maximum, lambda a, b: max(a, b))

    def test_min(self):
        self._subtest_binop(isa.Minimum, lambda a, b: min(a, b))

    def test_and(self):
        self._subtest_binop(isa.And, lambda a, b: a & b)

    def test_or(self):
        self._subtest_binop(isa.Or, lambda a, b: a | b)

    def test_xor(self):
        self._subtest_binop(isa.Xor, lambda a, b: a ^ b)

    def test_shl(self):
        self._subtest_binop(isa.ShiftLeft, lambda a, b: a << b)

    def test_shr(self):
        self._subtest_binop(isa.ShiftRight, lambda a, b: a >> b)

    def test_eq(self):
        self._subtest_binop(isa.Equal, lambda a, b: 1 if a == b else 0)

    def test_neq(self):
        self._subtest_binop(isa.NotEqual, lambda a, b: 1 if a != b else 0)

    def test_lt(self):
        self._subtest_binop(isa.LessThan, lambda a, b: 1 if a < b else 0)

    def test_le(self):
        self._subtest_binop(isa.LessOrEqual, lambda a, b: 1 if a <= b else 0)

    def test_gt(self):
        self._subtest_binop(isa.GreaterThan, lambda a, b: 1 if a > b else 0)

    def test_ge(self):
        self._subtest_binop(isa.GreaterOrEqual, lambda a, b: 1 if a >= b else 0)

    def _subtest_unop(self, ins_type, f):
        vm = VM()
        program = [ins_type()]
        for arg in (1, 2, 8, 16, 32, 64, 128):
            vm.load_program(program)
            vm.ctx.operands_stack.append(arg)
            vm.next()
            self.assertEqual(vm.ctx.operands_stack[0], f(arg))

    def test_inc(self):
        self._subtest_unop(isa.Increment, lambda arg: arg + 1)

    def test_dec(self):
        self._subtest_unop(isa.Decrement, lambda arg: arg - 1)

    def test_not(self):
        self._subtest_unop(isa.Not, lambda arg: ~arg)


if __name__ == '__main__':
    unittest.main()
