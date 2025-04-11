#include <stdio.h>
#include <stdlib.h>

#define MAX_NAME 256
#define TABLE_SIZE 10

typedef struct {
  char name[MAX_NAME];
  int age;
  // more stuff
} person;

unsigned int hash(char *name) {
  return 5;
}

int main(void) {
  printf("Jacob => %u\n", hash("Jacob"));
  printf("Sarah => %u\n", hash("Sarah"));
  printf("Joel => %u\n", hash("Joel"));
  printf("John => %u\n", hash("John"));
  printf("Talia => %u\n", hash("Talia"));


  return 0;
}
