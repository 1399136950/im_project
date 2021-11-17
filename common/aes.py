from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def aes_encrypt(src_str: str, key: bytes, mode=AES.MODE_CBC,  iv: bytes = None):
    """

    @param src_str:
    @param key:
    @param mode:
    @param iv:
    @return:
    """
    src_bytes = src_str.encode('utf-8')
    cipher = AES.new(key, mode, iv)
    cipher_text = cipher.encrypt(pad(src_bytes, 16))
    return cipher_text


def aes_decrypt(cipher_text: bytes, key: bytes, mode=AES.MODE_CBC, iv: bytes = None):
    """
    Aes解密
    @param cipher_text:
    @param key:
    @param mode:
    @param iv:
    @return:
    """
    cipher = AES.new(key, mode, iv)
    try:
        decipher = cipher.decrypt(cipher_text)
    except Exception as e:
        print(cipher_text, len(cipher_text))
        raise ValueError('cipher') from e
    text = unpad(decipher, block_size=16)    # 去补位
    return text
