from app import app

from hashlib import pbkdf2_hmac
from binascii import hexlify
from os import urandom

def hash_password(password, salt):
    """ Compute the hash of a given password with the given salt.

    This function exists as a convenient wrapper around "hashlib.pbkdf2_hmac".

    Arguments:
        password (type: utf-8 string):
            The password to hash.
        salt (type: bytes):
            The salt to use for hashing the password.

    Returns:
        The result is a "bytes" object, and should be passed through
        "binascii.hexlify" before transport or storage in the database.
    """
    return pbkdf2_hmac(
            app.config['CRYPTO']['HASHING']['ALGORITHM'],
            bytes(password, 'utf-8'), salt,
            app.config['CRYPTO']['HASHING']['ROUNDS'],
            app.config['CRYPTO']['HASHING']['KEY_LENGTH'])

def make_salt():
    """ Generate a suitable salt for use by "hash_password".

    This is a convenience wrapper around "os.urandom" that supplies the
    configuration option "CRYPTO.HASHING.SALT_LENGTH" as the number of bytes to
    get.

    Returns:
        The returned value is of type "bytes", and should be passed through
        "binascii.hexlify" before transport or storage.
    """
    salt = urandom(
            app.config['CRYPTO']['HASHING']['SALT_LENGTH'])
    return salt

def make_password(password):
    """ Given a plaintext password, create a new random salt and hash the
    password with it.

    Arguments:
        password (type: utf-8 string):
            The password to hash.

    Returns:
        A tuple with the first component being the hashed password as a bytes
        object and the second component being the salt as a bytes object.
    """
    salt = make_salt()
    hashed_password = hash_password(password, salt)
    return hashed_password, salt
