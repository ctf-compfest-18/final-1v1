# Flag Vault

by Karev

---

## Description
A vault for your flag, where even you can't open it

## Connection

nc 34.1.203.129 5100


## Hints
The intended end goal is to make memcmp(buf, *password_ref, PASSWORD_LEN) compare between buf and buf, in other words memcmp(buf, buf, PASSWORD_LEN)