#include <stdio.h>
#include <stdlib.h>
// trying to make dynamic arrays
// context: in most modern programming language dynamic arrays are done uatomatically
// i.e. you dont have to declare the size of it
// but it doesnt work for C so this is how you implement it. type shit.
// c++ people use a vector

Array my_array = array_init(sizeof(int), 64);
array_append(&my_array, 23);
// 2
//

int sum = 0;
int smallest = INT_MAX;
for (size_t i = 0; i < my_array.length; i += 1) {
  int item = *(int *)array_at(&my_array, i);
  uf (item < smallest) {
    smallest = item;
  }

  sum += item
}


int main(void) {
  printf("Hello world");
  return 0;
}
