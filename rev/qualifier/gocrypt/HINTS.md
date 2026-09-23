- okay so its AES CTR which is pretty weak if you reuse the nonce. Maybe we could do something about that

- just make a file with null bytes and patch/instrument it so it reuses the same nonce as the encrypted flag. the result will be the XOR keystream


