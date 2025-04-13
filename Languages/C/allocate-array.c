#include <stdio.h>
#include <stdlib.h>

int main(void){
  /*int array[3][3] =*/
  /*{{1,2,3},*/
  /*{4,5,6},*/
  /*{7,8,9}};// 2darray*/

  int **array = malloc(sizeof(int * ) * 3);
  
  for (int i = 0; i < 3; i++) {
    array[i] = malloc(sizeof(int) *3);
  }

  array[1][2] = 5;

  printf("%d", array[1][2]);

  return 0;
}
