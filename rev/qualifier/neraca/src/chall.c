#include <stdio.h>
#include <stdint.h>
#include <string.h>

int main(void)
{
    char in[64];

    printf("kunci: ");
    if (!fgets(in, sizeof(in), stdin))
        return 1;
    in[strcspn(in, "\n")] = '\0';

    if (strlen(in) != 28 || memcmp(in, "COMPFEST18{", 11) != 0 || in[27] != '}') {
        puts("timpang");
        return 1;
    }

    uint32_t x0  = (uint8_t)in[11];
    uint32_t x1  = (uint8_t)in[12];
    uint32_t x2  = (uint8_t)in[13];
    uint32_t x3  = (uint8_t)in[14];
    uint32_t x4  = (uint8_t)in[15];
    uint32_t x5  = (uint8_t)in[16];
    uint32_t x6  = (uint8_t)in[17];
    uint32_t x7  = (uint8_t)in[18];
    uint32_t x8  = (uint8_t)in[19];
    uint32_t x9  = (uint8_t)in[20];
    uint32_t x10 = (uint8_t)in[21];
    uint32_t x11 = (uint8_t)in[22];
    uint32_t x12 = (uint8_t)in[23];
    uint32_t x13 = (uint8_t)in[24];
    uint32_t x14 = (uint8_t)in[25];
    uint32_t x15 = (uint8_t)in[26];

    uint32_t e1 = 16777216u*x4 + 262144u*x1 + 4096u*x2 + 64u*x0 + x3;
    uint32_t e2 = 16777216u*x4 + 262144u*x7 + 4096u*x5 + 64u*x6 + x8;
    uint32_t e3 = 16777216u*x11 + 262144u*x9 + 4096u*x8 + 64u*x10 + x12;
    uint32_t e4 = 16777216u*x13 + 262144u*x12 + 4096u*x0 + 64u*x15 + x14;
    uint32_t e5 = 16777216u*x15 + 262144u*x5 + 4096u*x9 + 64u*x13 + x2;
    uint32_t e6 = x1 ^ x3 ^ x7 ^ x11 ^ x14;

    int ok = (e1 == 819072739u)
           & (e2 == 837007368u)
           & (e3 == 1869125647u)
           & (e4 == 1430499327u)
           & (e5 == 1089316191u)
           & (e6 == 118u);

    puts(ok ? "seimbang" : "timpang");
    return ok ? 0 : 1;
}
