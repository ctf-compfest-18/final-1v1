#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

__asm__(".global gadgets\ngadgets:\npop %rax\nret\nsyscall\nret\n");

char g_name[16];

static void set_name(void)
{
    printf("name (16): ");
    read(0, g_name, 16);
}

static void leave_message(void)
{
    char buf[0x20];
    printf("message: ");
    read(0, buf, 0x400);
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
