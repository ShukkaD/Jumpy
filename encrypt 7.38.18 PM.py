import os
from cryptography.fernet import Fernet

key = Fernet.generate_key()


class Encrypt():
    def __init__(self, file):
        global key
        base_dir = os.path.dirname(file)
        self.file = os.path.join(base_dir, file)
        self.key = key
        with open(os.path.join(base_dir, 'key'), 'wb') as filekey:
            filekey.write(self.key)
        self.fernet = Fernet(key)
        with open(self.file, 'rb') as file:
            original = file.read()

        encrypted = self.fernet.encrypt(original)

        with open(self.file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)


class Decrypt():
    def __init__(self, file, key_file):
        base_dir = os.path.dirname(file)
        self.file = os.path.join(base_dir, file)
        self.key_file = os.path.join(base_dir, key_file)

        # Load the key from the key file
        with open(self.key_file, 'rb') as keyfile:
            self.key = keyfile.read()

        # Using the key for decryption
        self.fernet = Fernet(self.key)

        # Opening the encrypted file
        with open(self.file, 'rb') as enc_file:
            encrypted = enc_file.read()

        # Decrypting the file
        decrypted = self.fernet.decrypt(encrypted)

        # Opening the file in write mode and writing the decrypted data
        with open(self.file, 'wb') as dec_file:
            dec_file.write(decrypted)
