# coding:utf-8
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AESCrypto(object):

    # AES_CBC_KEY = os.urandom(32)
    # AES_CBC_IV = os.urandom(16)
    KEY = b'+Rl\x86\xc6\x87\xe1&\x02\xdd\x1f\xa5\x1eK\xbdD\x03\x9f\xa4?E\xdf\xfcqT\x84\x06-\xd8v\x0f\xd0'
    IV = b'\xaf\x89i\xe6Pr\x1cd\xf6\x1eu\xee\x80\x99>~'
    @classmethod
    def encrypt(cls, data, mode='cbc'):
        func_name = '{}_encrypt'.format(mode)
        func = getattr(cls, func_name)
        return func(data)

    @classmethod
    def decrypt(cls, data, mode='cbc'):
        func_name = '{}_decrypt'.format(mode)
        func = getattr(cls, func_name)
        return func(data)

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @classmethod
    def cbc_encrypt(cls, data):
        if not isinstance(data, bytes):
            data = data.encode()
        cipher = Cipher(algorithms.AES(cls.KEY), modes.CBC(cls.IV), backend=default_backend())
        encryptor = cipher.encryptor()

        padded_data = encryptor.update(cls.pkcs7_padding(data))

        return padded_data

    @classmethod
    def cbc_decrypt(cls, data):
        if not isinstance(data, bytes):
            data = data.encode()
        cipher = Cipher(algorithms.AES(cls.KEY), modes.CBC(cls.IV), backend=default_backend())
        # print(cls.AES_CBC_KEY, '解密KEY')
        # print(cls.AES_CBC_IV, '解密IV')

        decryptor = cipher.decryptor()

        uppaded_data = cls.pkcs7_unpadding(decryptor.update(data))

        uppaded_data = uppaded_data.decode()
        return uppaded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息!')
        else:
            return uppadded_data
    @staticmethod
    def doing(string):
        return eval(string)

if __name__ == '__main__':
    # x = str(AESCrypto.encrypt('123456'))
    # print (x)
    x =b'_R\\R`\xef|\xf0\x1e\x18\xe9\xf3\x04\x17{\xdf'
    xx = AESCrypto.decrypt((x))
    print (xx)
