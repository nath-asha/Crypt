# Import necessary libraries
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Setup the pairing group
group = PairingGroup('SS512')

# Initialize the ABE scheme
cpabe = CPabe_BSW07(group)

# System setup
def setup():
    (master_public_key, master_key) = cpabe.setup()
    return master_public_key, master_key

# Key generation for users based on attributes
def keygen(master_key, user_attributes):
    user_secret_key = cpabe.keygen(master_key, user_attributes)
    return user_secret_key

# Encrypt a file with an access policy
def encrypt_file(file_path, access_policy, master_public_key):
    # Read file content
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Generate a symmetric key for AES encryption
    symmetric_key = get_random_bytes(16)

    # Encrypt the file content using AES
    cipher = AES.new(symmetric_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(file_data)

    # Encrypt the symmetric key using ABE
    symmetric_key_encrypted = cpabe.encrypt(master_public_key, symmetric_key, access_policy)

    # Save the encrypted file and the encrypted symmetric key
    with open(file_path + '.enc', 'wb') as f:
        for x in (cipher.nonce, tag, ciphertext):
            f.write(x)

    with open(file_path + '.key', 'wb') as f:
        f.write(symmetric_key_encrypted)

    return file_path + '.enc', file_path + '.key'

# Decrypt a file if the user's attributes satisfy the access policy
def decrypt_file(enc_file_path, enc_key_path, user_secret_key):
    # Read the encrypted symmetric key
    with open(enc_key_path, 'rb') as f:
        symmetric_key_encrypted = f.read()

    # Decrypt the symmetric key using ABE
    symmetric_key = cpabe.decrypt(user_secret_key, symmetric_key_encrypted)

    # Read the encrypted file content
    with open(enc_file_path, 'rb') as f:
        nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]

    # Decrypt the file content using AES
    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce)
    file_data = cipher.decrypt_and_verify(ciphertext, tag)

    # Save the decrypted file
    dec_file_path = enc_file_path.replace('.enc', '.dec')
    with open(dec_file_path, 'wb') as f:
        f.write(file_data)

    return dec_file_path
