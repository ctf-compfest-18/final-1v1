from cryptography.fernet import Fernet

# 1. Baca kunci yang Anda ekstrak
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# 2. Baca file yang terenkripsi
with open("apayaa.png.enc", "rb") as enc_file:
    encrypted_data = enc_file.read()

# 3. Lakukan dekripsi
decrypted_data = cipher.decrypt(encrypted_data)

# 4. Simpan kembali sebagai gambar PNG normal
with open("apayaa.png", "wb") as dec_file:
    dec_file.write(decrypted_data)

print("[+] File apayaa.png berhasil dipulihkan! Silakan buka gambarnya.")