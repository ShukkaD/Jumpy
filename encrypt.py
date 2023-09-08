from cryptography.fernet import Fernet

key = Fernet.generate_key()

class Encrypt():
    def __init__(self, file):
        global key
        self.file = file
        self.key = key
        with open('key', 'wb') as filekey:
            filekey.write(self.key)
        self.fernet = Fernet(key)
        with open(self.file, 'rb') as file:
            original = file.read()

        encrypted = self.fernet.encrypt(original)

        with open(self.file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

class FileEncryptor():
    def __init__(self, key):
        self.fernet = Fernet(key)

    def is_encrypted(self, file_path):
        try:
            with open(file_path, 'rb') as enc_file:
                encrypted = enc_file.read()
            self.fernet.decrypt(encrypted)
            return True
        except Exception as e:
            # If an exception occurs during decryption, the file is not encrypted.
            return False

class Decrypt():
    def __init__(self, file, key_file):
        self.file = file
        self.key_file = key_file

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
