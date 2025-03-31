#include <stdio.h>

typedef unsigned char *byte_pointer;

int main(void)
{
  // basics of pointers code
  int age = 18;
  int *pAge = &age;

  printf("address of age %p\n", &age);
  printf("value of pointer %p\n", pAge);
  printf("value of age %d\n", age);

  printf("pointer dereferencing %d\n", *pAge); // dereferencing the pointer
  printf("size of age %lu bytes\n", sizeof(age));
  printf("size of pointer age %lu bytes\n", sizeof(pAge));
}

void show_bytes(byte_pointer start, int len)
{
  int i;
  for (i = 0; i < len; i++)
    printf(" %.2x", start[i]);
  printf("\n");
}

void show_int(int x)
{
  show_bytes((byte_pointer) &x, sizeof(int));
}

void show_float(float x)
{
  show_bytes((byte_pointer) &x, sizeof(float));
}

void show_pointer(void *x)
{
  show_bytes((byte_pointer) &x, sizeof(void *));
}
