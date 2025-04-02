#include <stdio.h>
#include <string.h>

typedef unsigned char *byte_pointer;

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

int *ip;

void test_show_bytes(int val)
{
  int ival = val;
  float fval = (float) ival;
  int *pval = &ival;

  show_int(ival);
  show_float(fval);
  show_pointer(pval);
}


int main(void)
{
  // basics of pointers code
  int age = 18;
  int *pAge = &age;

  test_show_bytes(12345);

  /*show_int(5);*/


  int val = 0x12345678;
  byte_pointer valp = (byte_pointer) &val;
  show_bytes(valp, 1); // A
  show_bytes(valp, 2);
  show_bytes(valp, 3);

  printf("\nWow! Sring\n");
  char *s = "ABCDEF";
  show_bytes(s, strlen(s));
  /*printf("address of age %p\n", &age);*/
  /*printf("value of pointer %p\n", pAge);*/
  /*printf("value of age %d\n", age);*/
  /**/
  /*printf("pointer dereferencing %d\n", *pAge); // dereferencing the pointer*/
  /*printf("size of age %lu bytes\n", sizeof(age));*/
  /*printf("size of pointer age %lu bytes\n", sizeof(pAge));*/
}

