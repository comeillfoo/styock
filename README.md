# styock

## Architecture

![styok-arch](/styok-arch.jpg)

## Examples

### Factorial

Program on Rusty (subset of Rust):
```rust
fn fact(n: usize) -> usize {
    if n == 0 {
        return 1;
    }
    fact(n - 1) * n
}

fn main() -> () {
    fact(11)
}
```

Rusty Assembly (only fronend stage - `-f` option):
```assembly
        call main
        stop
fact:
        store 0
        load 0
        push 0
        eq
        jift .1_then_utlbl
        jmp .0_fi_utlbl
.1_then_utlbl:
        push 1
        ret
.0_fi_utlbl:
        load 0
        push 1
        sub
        call fact
        load 0
        mul
        ret
main:
        push 11
        call fact
        ret
```

Rusty assembly (after backend stage):
```assembly
0:      call 17
1:      stop
2:      store 0
3:      load 0
4:      push 0
5:      eq
6:      jift 2
7:      jmp 3
8:      push 1
9:      ret
10:     load 0
11:     push 1
12:     sub
13:     call -11
14:     load 0
15:     mul
16:     ret
17:     push 42
18:     call -16
19:     ret
```

### Sum

Program on Rusty (subset of Rust):
```rust
fn main() -> () {
    let a = 11;
    let b = 4;
    let c = a + b;
}
```

Rusty Assembly (only fronend stage - `-f` option):
```assembly
        call main
        stop
main:
        push 11
        store 0
        push 4
        store 1
        load 0
        load 1
        add
        store 2
        ret
```

Rusty assembly (after backend stage):
```assembly
0:      call 2
1:      stop
2:      push 11
3:      store 0
4:      push 4
5:      store 1
6:      load 0
7:      load 1
8:      add
9:      store 2
10:     ret
```

### Euclidean algorithm

Program on Rusty (subset of Rust):
```rust
fn gcd(mut a: u32, mut b: u32) -> u32 {
    while a * b > 0 {
        if a > b {
            a %= b;
        } else {
            b = b % a;
        }
    }
    a + b
}

fn main() {
    let a = 6;
    let b = 4;
    let ans = gcd(a, b);
}
```

Rusty Assembly (only fronend stage - `-f` option):
```assembly
        call main
        stop
gcd:
        store 1
        store 0
        jmp .3_predlo_cond_utlbl
.2_predlo_enter_utlbl:
        load 0
        load 1
        gt
        jift .1_then_utlbl
        load 1
        load 0
        mod
        store 1
        jmp .0_fi_utlbl
.1_then_utlbl:
        load 1
        load 0
        mod
        store 0
.0_fi_utlbl:
.3_predlo_cond_utlbl:
        load 0
        load 1
        mul
        push 0
        gt
        jift .2_predlo_enter_utlbl
.4_predlo_exit_utlbl:
        load 0
        load 1
        add
        ret
main:
        push 6
        store 0
        push 4
        store 1
        load 0
        load 1
        call gcd
        store 2
        ret
```

Rusty assembly (after backend stage):
```assembly
0:      call 28
1:      stop
2:      store 1
3:      store 0
4:      jmp 14
5:      load 0
6:      load 1
7:      gt
8:      jift 6
9:      load 1
10:     load 0
11:     mod
12:     store 1
13:     jmp 5
14:     load 1
15:     load 0
16:     mod
17:     store 0
18:     load 0
19:     load 1
20:     mul
21:     push 0
22:     gt
23:     jift -18
24:     load 0
25:     load 1
26:     add
27:     ret
28:     push 6
29:     store 0
30:     push 4
31:     store 1
32:     load 0
33:     load 1
34:     call -32
35:     store 2
36:     ret
```

## Demo

## Factorial

```bash
python3 -m rusty run -v ./fact.rsyb
0000000000000000:	Call(0x11)
0000000000000011:	Push(0xb)
0000000000000012:	Call(0xfffffffffffffff0)
0000000000000002:	Store(0x0)
0000000000000003:	Load(0x0)
0000000000000004:	Push(0x0)
0000000000000005:	Equal
0000000000000006:	JumpIfTrue(0x2)
0000000000000007:	Jump(0x3)
000000000000000a:	Load(0x0)
000000000000000b:	Push(0x1)
000000000000000c:	Substract
000000000000000d:	Call(0xfffffffffffffff5)
0000000000000002:	Store(0x0)
0000000000000003:	Load(0x0)
0000000000000004:	Push(0x0)
0000000000000005:	Equal
0000000000000006:	JumpIfTrue(0x2)
0000000000000007:	Jump(0x3)
000000000000000a:	Load(0x0)
000000000000000b:	Push(0x1)
000000000000000c:	Substract
000000000000000d:	Call(0xfffffffffffffff5)
0000000000000002:	Store(0x0)
0000000000000003:	Load(0x0)
0000000000000004:	Push(0x0)
0000000000000005:	Equal
0000000000000006:	JumpIfTrue(0x2)
0000000000000007:	Jump(0x3)
000000000000000a:	Load(0x0)
000000000000000b:	Push(0x1)
000000000000000c:	Substract
.................
0000000000000008:	Push(0x1)
0000000000000009:	Return
000000000000000e:	Load(0x0)
000000000000000f:	Multiply
0000000000000010:	Return
.................
000000000000000e:	Load(0x0)
000000000000000f:	Multiply
0000000000000010:	Return
000000000000000e:	Load(0x0)
000000000000000f:	Multiply
0000000000000010:	Return
0000000000000013:	Return
0000000000000001:	Stop
#0	0x2611500
```

## Sources

1. [A stack-based virtual machine for physical devices.](https://www.cs.ox.ac.uk/people/alex.rogers/stack/Stack.pdf)
1. [compiler construction - Compiling local variables for a stack machine - Stack Overflow](https://stackoverflow.com/questions/24836530/compiling-local-variables-for-a-stack-machine)
1. [Stack Based Virtual Machines - 6 · Andrea Bergia's Website](https://andreabergia.com/blog/2015/04/stack-based-virtual-machines-6/)
1. [How do stack-based virtual machines store data? : r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/kexe04/how_do_stackbased_virtual_machines_store_data/)
