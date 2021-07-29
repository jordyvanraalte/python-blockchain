import os
import datetime
import json
import hashlib
import base64
import getpass

# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

"""
Author: Maurice Snoeren <macsnoeren(at)gmail.com>
Version: 0.1 beta (use at your own risk)
Date: 26-06-2021
"""

class BlockchainId:

    def __init__(self, file_blockchain_id="blockchain.id"):
        """BlockchainId constructor. This class implements the blockchain id that holds all the important information.
           It could be seen as some kind of wallet. This class will be used to create an identification on the blockchain
           and store it safely in a file. When the user starts the node again, a password is required to unlock the
           wallet."""

        self.file_blockchain_id = file_blockchain_id

        self.data = {}

        if os.path.isfile(file_blockchain_id):
            self.read_file_blockchain_id()

        else:
            self.create_file_blockchain_id()

    def read_file_blockchain_id(self):
        try:
            f = open(self.file_blockchain_id, "r")
            salt      = base64.b64decode( f.readline() )
            iv        = base64.b64decode( f.readline() )
            encrypted = base64.b64decode( f.readline() )
            f.close()

            password  = getpass.getpass("Enter the password to open your wallet: ")
            key       = hashlib.scrypt(bytes(password, 'utf-8'), salt=salt, n=1024, r=8, p=1, dklen=32) # derive a 32 byte key = 256 bit
            cipher    = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypted = unpad( cipher.decrypt(encrypted), AES.block_size )

            self.data = json.loads(decrypted)
            print(self.data)

        except FileNotFoundError:
            print("read_file_blockchain_id: The file is not present.")

        except:
            print("read_file_blockchain_id: Wrong password?!")

    def create_file_blockchain_id(self):
        print("You need to create your wallet for the blockchain.")
        name = input("What is your name: ")
        password1 = getpass.getpass("Enter a password to protect your identification: ")
        password2 = getpass.getpass("Re-enter your password: ")

        if password1 != password2:
            print("Password do not match!")
            
        else:
            # Derive a key from the password to increase entropy!
            salt      = os.urandom(32)
            key       = hashlib.scrypt(bytes(password1, 'utf-8'), salt=salt, n=1024, r=8, p=1, dklen=32) # derive a 32 byte key = 256 bit
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            id        = hashlib.sha3_512( bytes( str(salt)+str(key)+str(timestamp)+str(name), 'utf-8') ).hexdigest()

            self.data = { "created": timestamp, "name": name, "id": id }

            cipher    = AES.new(key, AES.MODE_CBC)
            encrypted = cipher.encrypt(pad(bytes( json.dumps(self.data), 'utf-8'), AES.block_size))

        try:
            f = open(self.file_blockchain_id, "w")
            f.write( str(base64.b64encode(salt).decode('utf-8')) + "\n" )
            f.write( str(base64.b64encode(cipher.iv).decode('utf-8')) + "\n" )
            f.write( str(base64.b64encode(encrypted).decode('utf-8')) + "\n" )
            f.close()
            
        except Exception as e:
            print("create_file_blockchain_id: Writing file failed: " + str(e))

    def is_valid(self):
        return "id" in self.data

    def get_id(self):
        return self.data["id"]