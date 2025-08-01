from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
import binascii
import time

corrkey = RSA.importKey('''\
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
JNrRuoEUXpabUzGB8QIDAQAB
-----END PUBLIC KEY-----''')

def getCorrespondPath(ts):
    cipher = PKCS1_OAEP.new(corrkey, SHA256)
    encrypted = cipher.encrypt(f'refresh_{ts}'.encode())
    return binascii.b2a_hex(encrypted).decode()

# 时间戳获取
# ts = round(time.time() * 1000)