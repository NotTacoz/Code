import java.util.*;
public class p {
  public static void main(String[] args) {
    Scanner sc = new Scanner(System.in); // wow new Scanner
    System.out.println("N of members attending: ");
    int ma = sc.nextInt();
    System.out.println("N of non-members attending: ");
    int nma = sc.nextInt();
    double money = ((double)nma*7.50 + 5.0*(double)ma);
    if (money >= 100) {
      System.out.println("SUCCESS!! " + money);
    } else {
      System.out.println("Demise. " + money);
    }
    System.out.println("fortnite balls");
  }
}
