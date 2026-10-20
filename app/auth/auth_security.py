from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

def hash_password(password):
    hashed_password = password_hash.hash(password)
    return hashed_password

def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)










