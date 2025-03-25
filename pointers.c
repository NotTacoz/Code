#include <stdio.h>


int main(void)
{
  int i, *p;
  i = 10;
  p = &i; // points the ponter p to memory i

  printf("%d%d\n", *p, i);

  return 0;
}
