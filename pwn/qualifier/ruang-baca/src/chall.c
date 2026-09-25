#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <seccomp.h>

__asm__(".global gadgets\n"
        "gadgets:\n"
        "pop %rdi\nret\n"
        "pop %rsi\nret\n"
        "pop %rdx\nret\n"
        "pop %rax\nret\n"
        "syscall\nret\n");

char scratch[0x100];

const char FLAG_PATH[] = "/flag.txt";

static void lock_down(void)
{
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
    if (!ctx)
        exit(1);

    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open),       0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read),       0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write),      0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(close),      0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);

    if (seccomp_load(ctx) < 0)
        exit(1);
}

static void desk(void)
{
    char buf[0x40];
    printf("pesan  > ");
    read(0, buf, 0x200);
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);

    puts("=== Ruang Baca ===");
    printf("Arsip          : %s\n", FLAG_PATH);
    printf("Kertas catatan : %p\n", (void *)scratch);

    lock_down();
    desk();
    return 0;
}
