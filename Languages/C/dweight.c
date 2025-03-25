/* compute the dimensional weight of a 12x10x8" box"*/
#include <stdio.h>

int main(void) {
  int volume;

  int height = 8;
  int length = 12;
  int width = 10;
  volume = height * width * length;
 
  printf("dimensions: %dx%dx%d\n", length, width, height);
  printf("volume (cubic inches) %d\n", volume);
  printf("dimensional weight (pounds): %d\n", (volume + 165) / 166);
  
  return 0;
}
