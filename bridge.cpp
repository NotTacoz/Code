#include <iostream>
#include <vector>
#include <string>

int main(void) {
	std::string name, quest, colour;
	std::cout << "Welcome to the bridge of death\n";
	std::cout << "\nWhat is your name? ";
	std::cin >> name;
	std::cout << "\nWhat is your quest? ";
	std::cin >> quest;
	std::cout << "\nWhat is your favourite colour? ";
	std::cin >> colour;

	std::cout << name;
	std::cout << quest;
	std::cout << colour;

	return 0;
}
