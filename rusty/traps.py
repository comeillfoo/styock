#!/usr/bin/env python3
'''Описание "ловушек" для данной стековой виртуальной машины. Они прерывают
исполнение дальнейших инструкций вычислителя при возникновении чрезвычайных
условий. Например:

1. попытка получения операнда из пустого стека;
2. попытка выполнить инструкцию по некорретному адресу - за пределами памяти;
3. попытка декодировать неизвестную (некорректную) инструкцию;
4. попытка деления на ноль - справедливо для инструкций div и mod.
'''

class Trap(Exception):
    '''Common class for traps
    '''
    pass


class StackUnderflowTrap(Trap):
    '''Thrown if not enough operands are presented on the stack. This trap is
    applicable to any instruction that consumes operands from the stack like
    add, sub, div, mul, mod, max and etc.
    '''
    pass


class InvalidAddressTrap(Trap):
    '''Thrown if there was an attempt to access address outside of memory.
    '''
    def __init__(self, address: int):
        '''Constructor

        :param address: numerical address in memory
        :type address: int
        '''
        super().__init__(f'invalid address[{hex(address)}] accessed')


class IllegalInstructionTrap(Trap):
    '''This trap can be thrown while decoding instructions from the byte-array.
    Thrown if provided byte-sequence cannot be matched to any supported instruction.
    '''
    pass


class ZeroDivisionTrap(Trap):
    '''Thrown if an attempt of division by zero. This trap could occure while
    executing div or mod instruction.
    '''
    pass
