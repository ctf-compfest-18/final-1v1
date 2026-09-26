# Relay Receipt

Password: `CF-Final-b0541a21c5bcc3f7b902`


Hint 2: `Kalau sudah dapat rahasia dari direktori, ubah ke bytes dengan panjang tepat 32 byte, lalu cek cara chall.py membentuk kunci untuk membuka delivery. Di dalamnya ada dua ciphertext RSA dengan modulus yang sama. Perhatikan kedua eksponennya, bisa cari bilangan bulat u dan v sehingga u x e1 + v x e2 = 1?`

Hint 3: `Setelah policy terbuka, perhatikan hubungan kedua nonce. Mulai dari persamaan ECDSA s x k = z + r x d (mod n), dengan z sebagai hash pesan dan n sebagai order P-256. Tulis persamaan untuk masing-masing signature, lalu substitusikan hubungan nonce tadi. Coba eliminasi nonce sampai yang tersisa hanya private key d.`
