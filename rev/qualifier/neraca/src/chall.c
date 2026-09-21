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

    uint32_t e1 = 13845841u*x4 + 226981u*x1 + 3721u*x2 + 61u*x0 + x3;
    uint32_t e2 = 20151121u*x4 + 300763u*x7 + 4489u*x5 + 67u*x6 + x8;
    uint32_t e3 = 25411681u*x11 + 357911u*x9 + 5041u*x8 + 71u*x10 + x12;
    uint32_t e4 = 28398241u*x13 + 389017u*x12 + 5329u*x0 + 73u*x15 + x14;
    uint32_t e5 = 28398241u*x15 + 389017u*x5 + 5329u*x9 + 73u*x13 + x2;
    uint32_t e6 = x1 ^ x3 ^ x7 ^ x11 ^ x14;

    int ok = (e1 == 676537435u)
           & (e2 == 1003598700u)
           & (e3 == 2827508765u)
           & (e4 == 2416839387u)
           & (e5 == 1837029765u)
           & (e6 == 118u);

    puts(ok ? "seimbang" : "timpang");
    return ok ? 0 : 1;
}
