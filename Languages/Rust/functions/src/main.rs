fn main() {
    println!("Hello, world!");

    //another_function(5);
    //print_label_measurements(5, 'h');

    //let y = 6;
    let x = (let y = 6);
}

fn another_function(x: i32) {
    println!("the value of x is {x}");
}

fn print_label_measurements(x: i32, c: char) {
    println!("the measurement is {x}{c}");
}
