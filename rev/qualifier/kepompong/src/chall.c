#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#include "stage2_blob.h"

static const unsigned char KEY[8] = {
    0x9A, 0x47, 0xC3, 0x1E, 0x75, 0xB2, 0x6D, 0x08
};

int main(void)
{
    unsigned char in[128];
    void *page;
    unsigned long (*stage2)(const unsigned char *);
    unsigned int i;

    printf("kunci: ");
    fflush(stdout);
    if (!fgets((char *)in, sizeof(in), stdin)) {
        return 1;
    }
    in[strcspn((char *)in, "\n")] = '\0';

    if (strlen((char *)in) != 52 ||
        memcmp(in, "COMPFEST18{", 11) != 0 ||
        in[51] != '}') {
        puts("belum");
        return 1;
    }

    page = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED) {
        return 1;
    }

    for (i = 0; i < stage2_enc_len; i++) {
        ((unsigned char *)page)[i] = stage2_enc[i] ^ KEY[i % sizeof(KEY)];
    }

    stage2 = (unsigned long (*)(const unsigned char *))page;
    puts(stage2(in + 11) ? "mekar" : "belum");
    return 0;
}
