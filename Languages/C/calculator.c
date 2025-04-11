#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int add(double a, double b) {
  return a + b;
};

int subtract(double a, double b) {
  return (a - b);
};

int multiply(double a, double b) {
  return a * b;
};

int divide(double a, double b) {
  return a/b;
};

int main(void) {
  char vcontinue;
  printf("What would you like to do? (A)dd (S)ubtract (M)ultiply (D)ivide or e(X)it: ");
  scanf("%c", &vcontinue);
  
  printf("%c\n", vcontinue);

  while (strcmp(&vcontinue, "X") != 0) {
    int n1, n2;
    printf("enter the value of n1 and n2:");
    scanf("%d %d", &n1, &n2);
    if (strcmp(&vcontinue, "A") == 0) printf("%d\n",add(n1,n2));
    if (strcmp(&vcontinue, "S") == 0) printf("%d\n",subtract(n1,n2));
    if (strcmp(&vcontinue, "M") == 0) printf("%d\n",multiply(n1,n2));
    if (strcmp(&vcontinue, "D") == 0) printf("%d\n", divide(n1,n2));
    printf("What would you like to do? (A)dd (S)ubtract (M)ultiply (D)ivide or e(X)it: ");
    scanf("%c", &vcontinue);
  };

  printf("thanks for playin");

  return 0;
}
