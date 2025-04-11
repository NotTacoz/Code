#include <stdio.h>
#include <stdlib.h>
// trying to make dynamic arrays
// context: in most modern programming language dynamic arrays are done uatomatically
// i.e. you dont have to declare the size of it
// but it doesnt work for C so this is how you implement it. type shit.
// c++ people use a vector

int* arr;
size_t arrSize = 256;

// 1) Do you need an array used in many othe rplaces
// 2) Do you know the max amount of elements
// 3) Is that max amount too big (and waste memory)



int main(void) {
  arr = calloc(arrSize, sizeof(int));
  if (arr == NULL) {
    fprintf(stderr, "Array not allocated!");
    return 1;
  }

  arr[10] = 17;
  printf("Hello world %d\n", arr[10]);

  arrSize *= 2;
  arr = realloc(arr, arrSize * sizeof(int));

  free(arr);
  return 0;
}
