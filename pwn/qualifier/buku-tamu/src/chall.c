// PWN 1 - SROP.  Ubuntu 22.04 / x86-64.
// Build: see Makefile (flags are pinned there, not here).
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// The entire gadget supply of this binary.  Two gadgets, nothing else:
//   gadgets+0 : pop rax ; ret
//   gadgets+2 : syscall ; ret
__asm__(".global gadgets\ngadgets:\npop %rax\nret\nsyscall\nret\n");

char g_name[16];

static void set_name(void)
{
    printf("name (16): ");
    read(0, g_name, 16);          // raw read: no NUL handling, no length fixup
}

static void leave_message(void)
{
    char buf[0x20];
    printf("message: ");
    read(0, buf, 0x400);          // 0x400 into 0x20.  that's the bug.
}

static int menu(void)
{
    char c[16] = {0};

    printf("\n1) set name\n2) leave message\n> ");
    if (read(0, c, sizeof(c) - 1) <= 0)
        exit(0);
    return atoi(c);
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);

    for (;;) {
        switch (menu()) {
        case 1:  set_name();      break;
        case 2:  leave_message(); break;
        default: puts("?");       break;
        }
    }
}
