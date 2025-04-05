#include <stdio.h>
#include <stdlib.h>

int main(void){
  int n;
  printf("Enter array size: ");
  scanf("%d", &n);

  int *arr = malloc(n * sizeof(int)); // allocates memory of n integers
  if (!arr) {
    printf("Memory alloc failed\n");
    return 1;
  }

  for (int i = 0; i < n; i++) arr[i] = i*10; // set arr to [0, 10, 20, 30..100]

  for (int i = 0; i < n; i++) printf("%d", arr[i]); //print array
  printf("\n");

  free(arr); //frees memory
  return 0;
}
