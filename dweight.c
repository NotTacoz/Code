/* compute the dimensional weight of a 12x10x8" box"*/
#include <stdio.h>

int main(void) {
  int height, weight, length, width, volume;

  height = 8;
  length = 12;
  width = 10;
  volume = height * width * length;
  weight = (volume + 165) / 166;

  printf("dimensions: %dx%dx%d\n", length, width, height);
  printf("Volume (cubic inches) %d\n", volume);
  printf("Dimensional weight (pounds): %d\n", weight);
  
  return 0;
}
