package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"math/bits"
	"os"
)

var keyState = [8]uint32{
	0xb7e15163, 0x8aed2a6a, 0xbf715880, 0x9cf4f3c7,
	0x62e7160f, 0x38b4da56, 0xa784d904, 0x5190cfef,
}

var keyNoise = [16]uint32{
	0x243f6a88, 0x85a308d3, 0x13198a2e, 0x03707344,
	0xa4093822, 0x299f31d0, 0x082efa98, 0xec4e6c89,
	0x452821e6, 0x38d01377, 0xbe5466cf, 0x34e90c6c,
	0xc0ac29b7, 0xc97c50dd, 0x3f84d5b5, 0xb5470917,
}

func deriveKey() []byte {
	state := keyState
	for round := uint32(0); round < 0x6000; round++ {
		i := int((round ^ (round >> 3)) & 7)
		j := (i + int(state[(i+3)&7]&7) + 1) & 7
		x := state[i] + keyNoise[(round+uint32(i))&15] + round*0x9e3779b9
		y := state[j] ^ keyNoise[(round>>4)&15]
		state[i] = bits.RotateLeft32(x^y, int((round^y)&31)) + state[(j+5)&7]
		state[j] ^= bits.RotateLeft32(state[i]+round, int((x>>27)+1))
	}

	material := make([]byte, 96)
	for i, value := range state {
		binary.LittleEndian.PutUint32(material[i*4:], value)
	}
	for i, value := range keyNoise {
		binary.LittleEndian.PutUint32(material[32+i*4:], value^state[i&7])
	}
	digest := sha256.Sum256(material)
	return digest[:]
}

func main() {
	data, err := os.ReadFile(os.Args[1])
	if err != nil {
		panic(err)
	}

	block, err := aes.NewCipher(deriveKey())
	if err != nil {
		panic(err)
	}

	plaintext := make([]byte, len(data)-24)
	stream := cipher.NewCTR(block, data[8:24])
	stream.XORKeyStream(plaintext, data[24:])
	fmt.Print(string(plaintext))
}
