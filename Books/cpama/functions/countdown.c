#include <stdio.h>

int main(void) {
  double x;
  printf("enter countdown n: ");
  scanf("%lf", &x);

  printf("count down is %f", x);
  for (int i = x; i > 0; --i) {
    printf("%d seconds until liftoff!\n", i);
  }

  printf("liftoff!!\n");

  return 0;
}
