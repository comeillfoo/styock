fn fact(n: usize) -> usize {
    if n == 0 {
        return 1;
    }
    return fact(n - 1) * n;
}

fn main() -> () {

}