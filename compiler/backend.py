#!/usr/bin/env python3
from typing import Tuple
from functools import reduce


StateT = Tuple[int, dict[str, int]]


def is_label(line: str) -> bool:
    return line.endswith(':')


def fold_labels(state: StateT, line: str) -> StateT:
    ip, labels = state
    if not is_label(line):
        return (ip + 1, labels)

    label = line.rstrip(':').strip()
    if label in labels:
        raise Exception # duplicate label
    labels[label] = ip
    return (ip, labels)


def is_changes_ip(ins: str) -> bool:
    return reduce(lambda res, prefix: res or ins.startswith(prefix),
                  ['call', 'jmp', 'jift'], False)


def prepend_ip(ip: int, line: str, should_prepend: bool) -> str:
    if not should_prepend:
        return line
    return f'{ip}:{line}'


def process_instruction(ip: int, labels: dict[str, int], line: str,
                        should_prepend: bool) -> str:
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
