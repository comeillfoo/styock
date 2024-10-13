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

}
```

Rusty Assembly:
```assembly
fact:
        push n
        push 0
        cmp
        push 0
        cmp
        jnz fi_label
        push 1
        ret
fi_label:
        push n
        push 1
        sub
        call fact
        push n
        mul
main:

```
