from rsa                  import PublicKey, encrypt as rsae
from binascii import hexlify, unhexlify
from get_key import get_key
from rsa import pkcs1

def chrlen( n: str) -> str:
        return chr(len(n))

def encrypt(json, mail, pw):
        string  = f"{chrlen(json['sessionKey'])}{json['sessionKey']}{chrlen(mail)}{mail}{chrlen(pw)}{pw}".encode()
        mod     = int(json['nvalue'], 16)
        evl     = int(json['evalue'], 16)
        pbk     = PublicKey(evl, mod)
        out     = rsae(string, pbk)

        return hexlify(out).decode('utf-8')


if __name__ == "__main__":
    print(encrypt(json=get_key(), mail="test@example.com", pw="password123"))