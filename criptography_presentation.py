from Crypto.Cipher import Blowfish

from constants import DEFAULT_KEY, ENCONDING_FORMAT

class BlowfishCriptography:

    def __init__(self, key):
        self.cipher = Blowfish.new(key)

    def __prepare_for_encryption(self, text):
        
        return text.ljust(8 * (len(text) // 8 + 1))

    def encrypt(self, plain_text):
        
        plain_text = self.__prepare_for_encryption(plain_text)
        return self.cipher.encrypt(plain_text)

    def decrypt(self, cipher_text):
       
        decrypted_text = self.cipher.decrypt(cipher_text).decode(ENCONDING_FORMAT)
        decrypted_text = decrypted_text.strip()
        return decrypted_text

if __name__ == '__main__':
    
    message = 'Alone on a Saturday night? God, you\'re pathetic'

    cipher = BlowfishCriptography(DEFAULT_KEY)

    encrypted_text = cipher.encrypt(message)
    decrypted_text = cipher.decrypt(encrypted_text)

    assert message == decrypted_text, 'Message are not equal after apply encrypt and decrypt methods'

    print("Emissor message: {}\n".format(message))
    print("Emissor key: {}\n".format(DEFAULT_KEY))
    print("Encrypted message: {}\n".format(encrypted_text))
    print("Receptor key: {}\n".format(DEFAULT_KEY))
    print("Receptor message: {}\n".format(decrypted_text))