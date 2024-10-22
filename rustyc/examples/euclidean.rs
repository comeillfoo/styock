fn gcd(mut a: u32, mut b: u32) -> u32 {
    while a * b > 0 {
        if a > b {
            a %= b;
            continue;
        }
        b = b % a;
    }
    a + b
}

fn main() {
    let a = 6;
    let b = 4;
    gcd(a, b)
}
