import java.util.*;
public class oddeven { 
  public static void is_even(int n) {
    if (n % 2 == 1) {
      System.out.println("ODD");
    } else if(n % 2 == 0) {
      System.out.println("EVEN");
    }
  }
  public static void main(String[] args) {
    Scanner sc = new Scanner(System.in); // wow new Scanner

    int[] numbers = new int[5];

    for (int i = 0; i < numbers.length; i++) { 
      System.out.println("Enter a number: ");
      numbers[i] = sc.nextInt();
    }
    
    for (int j : numbers) { 
      is_even(j);
    }

    System.out.println("fortnite balls");
  }
}
