#define GROUP(base, want)                                                     \
    do {                                                                      \
        unsigned long v = 0;                                                  \
        int i;                                                                \
        for (i = 0; i < 8; i++) {                                             \
            v |= (unsigned long)(unsigned char)(in[(base) + i] ^ k)           \
                 << (8 * i);                                                  \
            k = (unsigned char)(k * 31 + 17);                                 \
        }                                                                     \
        if (v != (want)) {                                                    \
            return 0;                                                         \
        }                                                                     \
    } while (0)

unsigned long check(const unsigned char *in)
{
    unsigned char k = 0x5B;

    GROUP(0,  0xC5132244C6D6633FUL);
    GROUP(8,  0x11CFA6C44E4CE484UL);
    GROUP(16, 0x8E243828DECF4968UL);
    GROUP(24, 0x429989EF0764E4EBUL);
    GROUP(32, 0xD748357586E47D38UL);

    return 1;
}
