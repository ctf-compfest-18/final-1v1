// regs
#define PC 0x5f
#define R1 0x6f
#define R2 0x7f
#define R3 0x8f
#define R4 0x9f
#define R5 0xaf

// ops
#define _MOV_IMM 0x30
#define _MOV_REG 0x31
// math ops
#define _ADD 0x40
#define _SUB 0x41
#define _XOR 0x42
// buffer things
#define _USER_BUF 0x60
// others
#define _EXIT_IF_NOT_EQUAL 0x70
#define _HALT 0xff
