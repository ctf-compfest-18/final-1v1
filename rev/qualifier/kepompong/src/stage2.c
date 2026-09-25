unsigned long check(const unsigned char *in)
{
    volatile unsigned char k0 = 0x5B;
    volatile unsigned char k1 = 0xA7;
    volatile unsigned char k2 = 0x3E;
    volatile unsigned char k3 = 0xC9;

    if ((in[ 0] ^ k0) != 0x3F) return 0;
    if ((in[ 1] ^ k1) != 0xD2) return 0;
    if ((in[ 2] ^ k2) != 0x53) return 0;
    if ((in[ 3] ^ k3) != 0xB9) return 0;
    if ((in[ 4] ^ k0) != 0x04) return 0;
    if ((in[ 5] ^ k1) != 0xD3) return 0;
    if ((in[ 6] ^ k2) != 0x56) return 0;
    if ((in[ 7] ^ k3) != 0xFA) return 0;
    if ((in[ 8] ^ k0) != 0x04) return 0;
    if ((in[ 9] ^ k1) != 0xD5) return 0;
    if ((in[10] ^ k2) != 0x49) return 0;
    if ((in[11] ^ k3) != 0xB1) return 0;
    if ((in[12] ^ k0) != 0x04) return 0;
    if ((in[13] ^ k1) != 0xD7) return 0;
    if ((in[14] ^ k2) != 0x0A) return 0;
    if ((in[15] ^ k3) != 0xAE) return 0;
    if ((in[16] ^ k0) != 0x68) return 0;
    if ((in[17] ^ k1) != 0xF8) return 0;
    if ((in[18] ^ k2) != 0x4A) return 0;
    if ((in[19] ^ k3) != 0xA1) return 0;
    if ((in[20] ^ k0) != 0x68) return 0;
    if ((in[21] ^ k1) != 0xC9) return 0;
    if ((in[22] ^ k2) != 0x61) return 0;
    if ((in[23] ^ k3) != 0xB1) return 0;
    if ((in[24] ^ k0) != 0x6B) return 0;
    if ((in[25] ^ k1) != 0xD5) return 0;
    if ((in[26] ^ k2) != 0x61) return 0;
    if ((in[27] ^ k3) != 0xF8) return 0;
    if ((in[28] ^ k0) != 0x2F) return 0;
    if ((in[29] ^ k1) != 0xF8) return 0;
    if ((in[30] ^ k2) != 0x5C) return 0;
    if ((in[31] ^ k3) != 0xFD) return 0;
    if ((in[32] ^ k0) != 0x38) return 0;
    if ((in[33] ^ k1) != 0xCC) return 0;
    if ((in[34] ^ k2) != 0x61) return 0;
    if ((in[35] ^ k3) != 0xF9) return 0;
    if ((in[36] ^ k0) != 0x35) return 0;
    if ((in[37] ^ k1) != 0xC4) return 0;
    if ((in[38] ^ k2) != 0x0D) return 0;
    if ((in[39] ^ k3) != 0xE8) return 0;

    return 1;
}
