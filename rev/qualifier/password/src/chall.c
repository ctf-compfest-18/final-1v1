#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

char flag[256];
char password[100];
void init() { srand(time(NULL) >> 1); }

void init_flag() {
  FILE *f = fopen("./flag.txt", "r");
  if (f == NULL) {
    printf("error, contact probset\n");
    exit(0);
  }
  fgets(flag, sizeof(flag), f);
}
unsigned long key[] = {0x1230841L,  0x184918249L, 0x8129489L,   0x918245L,
                       0x85935835L, 0xABBDEAFL,   0x2349843BBL, 0x348329AAL};

unsigned long someshit(unsigned long x) {
  unsigned long ret;
  for (int i = 0; i < 67; i++) {
    ret = ret ^ (i * 324 + x);
    if (i % 13 == 0) {
      ret ^= 67;
    }
    ret ^= rand() & 0x1234567;
  }
  return ret;
}

void makepass() {
  for (int i = 0; i < 8; i++) {
    snprintf((password + i * 4), 5, "%04lx", someshit(key[i]) & 0xffff);
  }
}

int main() {
  char buf[256];
  printf("whats da password my man? ");
  init();
  makepass();
  fgets(buf, 256, stdin);
  buf[strcspn(buf, "\n")] = 0;

  if (!strcmp(password, buf)) {
    init_flag();
    printf("here you go %s\n", flag);
  } else {
    printf("nah\n");
  }
}
