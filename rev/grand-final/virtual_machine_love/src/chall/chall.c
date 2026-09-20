#include "api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define u8 unsigned char
#define BUF_SZ 256
#define MAX_CODE (1 << 16)

u8 regs[256];
u8 user_buf[BUF_SZ];
u8 code[MAX_CODE];
int code_len;

void load_image(const char *path) {
  FILE *f = fopen(path, "rb");
  if (!f) {
    perror("fopen");
    exit(1);
  }
  // skip ppm header
  char line[64];
  fgets(line, sizeof(line), f); // P6
  fgets(line, sizeof(line), f); // W H
  fgets(line, sizeof(line), f); // 255
  code_len = fread(code, 1, MAX_CODE, f);
  fclose(f);
}

void run() {
  int ip = 0;
  while (ip + 2 < code_len) {
    u8 op = code[ip];
    u8 a = code[ip + 1];
    u8 b = code[ip + 2];
    ip += 3;

    switch (op) {
    case _MOV_IMM:
      regs[a] = b;
      break;
    case _MOV_REG:
      regs[a] = regs[b];
      break;
    case _ADD:
      regs[a] = regs[a] + regs[b];
      break;
    case _SUB:
      regs[a] = regs[a] - regs[b];
      break;
    case _XOR:
      regs[a] = regs[a] ^ regs[b];
      break;
    case _USER_BUF:
      regs[b] = user_buf[regs[a]];
      break;
    case _EXIT_IF_NOT_EQUAL:
      if (regs[a] != regs[b]) {
        printf("verdict: INCORRECT\n");
        exit(0);
      }
      break;
    case _HALT:
      printf("verdict: TRUE\n");
      exit(0);
    default:
      break;
    }
  }
}

int main() {
  char path[256];

  printf("vm image? ");
  fgets(path, sizeof(path), stdin);
  path[strcspn(path, "\n")] = 0;
  load_image(path);

  printf("vm user buffer? ");
  fgets((char *)user_buf, BUF_SZ, stdin);
  run();
}
