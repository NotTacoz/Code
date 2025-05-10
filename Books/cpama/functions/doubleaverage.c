#include <stdio.h>

double average(double a, double b)
{
  return (a+b) / 2;
}

int main(void) {
  printf("the average of 10 and 20 is: %g\n", average(10,20));

  double x, y, z;

  printf("Enter 3 numbers: ");
  scanf("%lf%lf%lf", &x, &y, &z);
  printf("average of %g and %g: %g\n", x, y, average(x,y));
  printf("average of %g and %g: %g\n", y, z, average(y,z));
  printf("average of %g and %g: %g\n", x, z, average(x,z));

  return 0;
}
