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
fact:
        load 0
        push 0
        eq
        jift 1_fi_label
        push 1
        ret
1_fi_label:
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

## Sources

1. [A stack-based virtual machine for physical devices.](https://www.cs.ox.ac.uk/people/alex.rogers/stack/Stack.pdf)
1. [compiler construction - Compiling local variables for a stack machine - Stack Overflow](https://stackoverflow.com/questions/24836530/compiling-local-variables-for-a-stack-machine)
1. [Stack Based Virtual Machines - 6 · Andrea Bergia's Website](https://andreabergia.com/blog/2015/04/stack-based-virtual-machines-6/)
1. [How do stack-based virtual machines store data? : r/learnprogramming](https://www.reddit.com/r/learnprogramming/comments/kexe04/how_do_stackbased_virtual_machines_store_data/)
