import os

from Crypto.Cipher import Blowfish

from constants import DEFAULT_KEY, ENCONDING_FORMAT


class BlowfishCriptography:
    def __init__(self, key):
        self.cipher = Blowfish.new(key)

    def __prepare_for_encryption(self, text):
        """
        Ensures the message length is multiple of 8

        :param text: The content to be prepared for encryption
        :type: str
        :return: The content padded with trailing space characters
        """
        return text.ljust(8 * (len(text) // 8 + 1))

    def encrypt(self, plain_text):
        """
        Encrypts the text

        :param plain_text: The text to be encrypted
        :type: str
        :return: Encrypted text using blowfish algorithm
        """
        plain_text = self.__prepare_for_encryption(plain_text)
        return self.cipher.encrypt(plain_text)

    def decrypt(self, cipher_text):
        """
        Decrypts the text. Also, decodes the decrypted text to UTF-8 and removes
        the trailing space characters

        :param cipher_text: The ciphered text to be decrypted
        :type: str
        :return: Decrypted text which was encrypted using Blowfish algorithm
        """
        decrypted_text = self.cipher.decrypt(cipher_text).decode(ENCONDING_FORMAT)
        decrypted_text = decrypted_text.strip()
        return decrypted_text


if __name__ == '__main__':
    message = 'Alone on a Saturday night? God, you\'re pathetic'

    cipher = BlowfishCriptography(DEFAULT_KEY)

    encrypted_text = cipher.encrypt(message)
    decrypted_text = cipher.decrypt(encrypted_text)

    assert message == decrypted_text, 'Message are not equal after apply encrypt and decrypt methods'
