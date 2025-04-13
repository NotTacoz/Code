use std::io;

fn main() {
    //let x = 5;
    //println!("The value of x is {x}");
    //let x = x + 1;
    //
    //{
    //    let x = x * 2;
    //    println!("The value of x in the inner scope is : {x}");
    //}
    //println!("The value of x is {x}");
    //

    //let x = 2.0; // f64
    //let y: f32 = 3.0; // f32
    
    // addition
    //let sum = 5 + 10;
    //
    //let difference = 95.5 - 4.3;
    //
    //let product = 4 * 30;
    //
    //let quotient = 56.7/32.2;
    //let truncated = -5/3;
    //
    ////remainder
    //let remainder = 43%5;
    //
    //println!("additon {sum} and difference {difference} and {product} product and {quotient} quotient and {truncated} truncated and {remainder} remainder");

    //let t = true;
    //let f: bool = false;
    //println!("{t}, {f}");
    //let tup: (i32, f64, u8) = (500, 6.4, 1);

    //let tup = (500, 6.4, 1);
    //let (x, y, z) = tup;
    //println!("the value of x,y,z is {x},{y},{z}");
    //let x: (i32, f64, u8) = (500, 6.4, 1);
    //
    //let five_hundred = x.0;
    //
    //let six_point_four = x.1;
    //
    //let one = x.2;
    //
    //println!("{} {} {}", five_hundred, six_point_four, one); 
    //

    //let a = [1, 2, 3, 4, 5];
    //let months = ["jan", "feb", "mar", "etc"];
    //let b: [i32; 5] = [1, 2, 3, 4, 5];
    //let c = [3; 5];
    //
    //println!("{a} {b} {c}");
    //
    let a = [1, 2, 3, 4, 5];

    println!("Please enter an array index.");

    let mut index = String::new();

    io::stdin()
        .read_line(&mut index)
        .expect("Failed to read a line");

    let index: usize = index
        .trim()
        .parse()
        .expect("Indec entered was no t a number");

    let element = a[index];

    println!("The value of the element at index {index} is: {element}");
}
