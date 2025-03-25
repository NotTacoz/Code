/* compute the dimensional weight of a 12x10x8" box"*/
#include <stdio.h>

#define INCHES_PER_POUND 166

int main(void) {
  int height, weight, length, width, volume;

  printf("Enter height of box: ");
  scanf("%d", &height);
  printf("Enter width of box: ");
  scanf("%d", &width);
  printf("Enter length of box: ");
  scanf("%d", &length);
  volume = height * width * length;
  weight = (volume + INCHES_PER_POUND) / INCHES_PER_POUND;

  printf("dimensions: %dx%dx%d\n", length, width, height);
  printf("Volume (cubic inches) %d\n", volume);
  printf("Dimensional weight (pounds): %d\n", weight);
  
  return 0;
}
