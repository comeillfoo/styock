#!/usr/bin/env python3
'''Модуль, реализующий второй этап трансляции входного файла в инструкции
виртуальной машины. В который входит, разрешение текстовых меток в конкретные
адреса. Функции данного модуля помогают пропатчить инструкции jmp, jift и call
выходной программы, заменяя читаемые текстовые метки разностями между адресом
метки в аргументе данной инструкции и адресом этой инструкции.

Например:
```
0x0: call main
0x1: stop
0x2: ret       # main:

```
становится
```
0x0: call 2    # 0x2 - 0x0 = 0x2
0x1: stop
0x2: ret       # main:
```
'''
from typing import Tuple
from functools import reduce


StateT = Tuple[int, dict[str, int]]


def is_label(line: str) -> bool:
    '''Checks if current line in program is label and not an instruction

    :param line: program's line
    :type line: str

    :return: true if line is label, false otherwise
    :rtype: bool
    '''
    return line.endswith(':')


def is_changes_ip(ins: str) -> bool:
    '''Checks if instruction changes instruction pointer. True for any kind of
    jumps and calling subprograms. Now returns true only for jmp, jift and call.

    :param ins: VM instruction
    :type ins: str

    :return: true if instruction changes IP, false - otherwise
    :rtype: bool
    '''
    return reduce(lambda res, prefix: res or ins.startswith(prefix),
                  ['call', 'jmp', 'jift'], False)


def prepend_ip(ip: int, line: str, should_prepend: bool) -> str:
    '''Prepends current value of instruction pointer to line if required.

    :param ip: current value of instruction pointer
    :type ip: int
    :param line: program's line
    :type line: str
    :param should_prepend: if false then function does nothing
    :type should_prepend: bool

    :return: prepended with IP or not line according to should_prepend
    :rtype: str
    '''
    if not should_prepend:
        return line
    return f'{ip}:{line}'


def fold_labels(state: StateT, line: str) -> StateT:
    '''Matches an IP to provided line and if line represents label then
    function accumulates it to map of labels.

    :param state: current value of IP and map of labels
    :type state: StateT alias to (int, dict[str, int])
    :param line: program's line
    :type line: str

    :return: updated state in dependence of label or not current line is
    :rtype: StateT
    '''
    ip, labels = state
    if not is_label(line):
        return (ip + 1, labels)

    label = line.rstrip(':').strip()
    if label in labels:
        raise Exception # duplicate label
    labels[label] = ip
    return (ip, labels)


def process_instruction(ip: int, labels: dict[str, int], line: str,
                        should_prepend: bool) -> str:
    '''Patches a single instruction by prepending its address if required and
    replaces labels with the relative address to these labels for jmp, jift and
    call instructions.

    :param ip: current IP value
    :type ip: int
    :param labels: map of labels
    :type labels: dict[str, int]
    :param line: current instruction to patch
    :type line: str
    :param should_prepend: should enumerate line with its address
    :type should_prepend: bool

    :return: patched line
    :rtype: str
    '''
    ins = line.strip()
    if not is_changes_ip(ins):
        return prepend_ip(ip, line, should_prepend)
    ins, label = ins.split(' ', 1)
    if label not in labels:
        print(ip, ins, label, labels)
        raise Exception # undefined label used

    return prepend_ip(ip, line.replace(label, str(labels[label] - ip)),
                      should_prepend)


def process(source: str, should_prepend: bool = False) -> str:
    '''Finds all labels in the program and matches them with its possible
    address (instruction pointer). Then patches jmp, jift and call instructions
    by replacing labels with the substraction between label's address and this
    instruction's address.

    :param source: program
    :type source: str
    :param should_prepend: should enumerate every instruction with corresponding
    instruction pointer value for debugging purposes
    :type should_prepend: bool, default False

    :return: patched program with resolved labels
    :rtype: str
    '''
    lines = source.split('\n')
    _, labels = reduce(fold_labels, lines, (0, {}))

    ip = 0
    instructions = []
    for line in lines:
        if is_label(line):
            continue
        instructions.append(process_instruction(ip, labels, line,
                                                should_prepend))
        ip += 1
    return '\n'.join(instructions)
