#include "api.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#define W 32
#define H 16
#define PATH "vm.ppm"
#define u8 unsigned char
#define LEN 32

/*
 *
 * vm specs
 *
 *
 * regs:
 * PC -> 0x5f
 * R1 -> 0x6f
 * R2 -> 0x7f
 * R3 -> 0x8f
 * R4 -> 0x9f
 * R5 -> 0xaf
 *
 *
 * op:
 * MOV_IMM -> (0x30, R, IMM)
 * MOV_REG -> (0x31, R1, R2)
 * ADD (0x40, R1, R2)
 * SUB (0x41, R1, R2)
 * XOR (0x42, R1, R2)
 *
 * USER_BUF (0x60, R1, R2)
 * > R1 : idx in buf
 * > R2 : output reg
 *
 *
 * EXIT_IF_NOT_EQUAL (0x70, R1, R2)
 * > R1 == R2 ?
 *
 * HALT (0xff, ?, ?)
 *
 */
FILE *f;
int counter;

static inline void op(u8 c, u8 r1, u8 r2) {
  fputc(c, f);
  fputc(r1, f);
  fputc(r2, f);
}

#define DEFOP(name, opcode)                                                    \
  static inline void name(u8 r1, u8 r2) { op(opcode, r1, r2); }

DEFOP(MOV_IMM, _MOV_IMM);
DEFOP(MOV_REG, _MOV_REG);

DEFOP(ADD, _ADD);
DEFOP(SUB, _SUB);
DEFOP(XOR, _XOR);

DEFOP(USER_BUF, _USER_BUF);
DEFOP(EXIT_IF_NOT_EQUAL, _EXIT_IF_NOT_EQUAL);

static inline void HALT() { op(0xff, 0xff, 0xff); }

u8 add_key[LEN];
u8 xor_key[LEN];
u8 res[LEN];
u8 flag[LEN];

void init_flag() {
  int fd = open("flag.bin", O_RDONLY);
  read(fd, flag, LEN);
  close(fd);
}

void init_params() {
  for (int i = 0; i < LEN; i++) {
    add_key[i] = rand() & 0x18;
    xor_key[i] = rand() & 0xff;
    res[i] = (flag[i] + add_key[i]) ^ (xor_key[i]);
  }
}

int main() {
  srandom(4815791);
  init_flag();
  init_params();
  f = fopen(PATH, "wb");
  fprintf(f, "P6\n");
  fprintf(f, "%d %d\n", W, H);
  fprintf(f, "255\n");

  for (int i = 0; i < LEN; i++) {
    MOV_IMM(R1, i);
    USER_BUF(R1, R2);
    MOV_IMM(R3, add_key[i]);
    ADD(R2, R3);
    MOV_IMM(R4, xor_key[i]);
    XOR(R2, R4);
    MOV_IMM(R1, res[i]);
    EXIT_IF_NOT_EQUAL(R1, R2);
  }

  HALT();
  for (int i = 0; i < (W * H - LEN); i++) {
    op(0, 0, 0);
  }

  printf("generated to %s\n", PATH);

  fclose(f);
}
