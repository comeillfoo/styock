# styock

## Frontend examples

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
    fact(42)
}
```

Rusty Assembly:
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
        push 42
        call fact
        ret
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

Rusty Assembly:
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

Rusty Assembly:
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

## Sources

1. [A stack-based virtual machine for physical devices.](https://www.cs.ox.ac.uk/people/alex.rogers/stack/Stack.pdf)
1. [compiler construction - Compiling local variables for a stack machine - Stack Overflow](https://stackoverflow.com/questions/24836530/compiling-local-variables-for-a-stack-machine)
1. [Stack Based Virtual Machines - 6 · Andrea Bergia's Website](https://andreabergia.com/blog/2015/04/stack-based-virtual-machines-6/)
1. [How do stack-based virtual machines store data? : r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/kexe04/how_do_stackbased_virtual_machines_store_data/)
