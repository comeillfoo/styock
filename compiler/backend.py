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


def is_change_ip(ins: str) -> bool:
    return reduce(lambda res, prefix: res or ins.startswith(prefix),
                  ['call', 'jmp', 'jift'], False)


def process_instruction(ip: int, labels: dict[str, int], line: str) -> str:
    ins = line.strip()
    if not is_change_ip(ins):
        return str(ip) + ':' + line
    ins, label = ins.split(' ', 1)
    if label not in labels:
        print(ip, ins, label, labels)
        raise Exception # undefined label used
    return str(ip) + ':' + line.replace(label, str(labels[label] - ip))


def process(source: str) -> str:
    lines = source.split('\n')
    _, labels = reduce(fold_labels, lines, (0, {}))

    ip = 0
    instructions = []
    for line in lines:
        if is_label(line):
            continue
        instructions.append(process_instruction(ip, labels, line))
        ip += 1
    return '\n'.join(instructions)
