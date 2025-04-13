#include <stdio.h>

typedef unsigned char *byte_pointer;

void show_bytes(byte_pointer start, int len) {
  for (int i =0; i<len; i++)
    printf("%.2x ", start[i]);
  printf("\n");
}
int main(void){
  int val = 0x12345678;
  byte_pointer valp = (byte_pointer) &val;
  show_bytes(valp,1);
  show_bytes(valp,2);
  show_bytes(valp,3);
  char *s = "ABCDEF";
  show_bytes(s, strlen(s));
}
