# -*- coding: utf-8

"""
加密处理

"""
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from config.conf import AES_KEY


# KEY = 'kdodl224434k3k22'  # produce
# KEY = '2sd8f96b9qjo7p76'  # dev
KEY = AES_KEY
IV = bytearray([2, 5, 2, 1, 8, 3, 0, 8, 9, 8, 3, 6, 2, 3, 2, 5])


def aes_encrypt(proto_bytes):
    """
    Proto 消息体 AES 加密处理
    :param proto_bytes: 原始二进制数据
    :return: 加密后二进制数据
    """
    key = KEY.encode('utf-8')
    mode = AES.MODE_CBC

    cipher = AES.new(key, mode, IV)
    cipher_text = cipher.encrypt(pad(proto_bytes, 16))

    return cipher_text


def aes_decrypt(cipher_text):
    """
    解密处理
    """
    key = KEY.encode('utf-8')
    mode = AES.MODE_CBC

    cipher = AES.new(key, mode, IV)
    try:
        decipher = cipher.decrypt(cipher_text)
    except Exception as e:
        print(cipher_text, len(cipher_text))
        raise ValueError('cipher') from e
    text = unpad(decipher, block_size=16)    # 去补位
    return text


if __name__ == '__main__':
    cipher = AES.new(KEY.encode('utf-8'), AES.MODE_CBC, IV)
    proto_bytes = b'hello world'
    cipher_text = cipher.encrypt(pad(proto_bytes, 16))
    print(cipher_text)
