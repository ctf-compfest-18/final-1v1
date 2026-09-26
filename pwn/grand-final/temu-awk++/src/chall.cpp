// g++ -O0 chall.cpp -o chall -fno-stack-protector
// what pie enabled? this is not the awk++ i was promised...
#include <cstdio>
#include <iostream>
#include <vector>

__attribute__((constructor))
void disable_buffering() {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);
}

// no win function too, i got scammed bruh
// void win() {
//   printf("Heres your flag: ");
//   system("cat flag.txt");
// }

void menu() {
  std::cout << "1. Add number to vector" << std::endl;
  std::cout << "2. View vector" << std::endl;
  std::cout << "3. Exit" << std::endl;
  std::cout << "> ";
}

int main() {
  std::vector<unsigned long long> vec;
  char buf[0x20];
  unsigned int choice;
  unsigned long long num, idx;
  vec.push_back(0x676767);

  printf("leak for you: %p\n", &vec[0]);

  while (true) {
    menu();
    std::cin >> buf;
    choice = std::atoi(buf);
    switch (choice) {
    case 1:
      std::cout << "Num: ";
      std::cin >> num;
      if (!std::cin.good())
        exit(0);
      vec.push_back(num);
      break;
    case 2:
      std::cout << "Idx: ";
      std::cin >> idx;
      if (!std::cin.good())
        exit(0);
      std::cout << vec[idx] << std::endl;
      break;
    case 3:
      std::cout << "okay bro\n";
      return 0;

    default:
      printf("what?\n");
      break;
    }
  }
}
