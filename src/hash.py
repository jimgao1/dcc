import hashlib

def hash(data):
    m = hashlib.sha256()
    m.update(data)
    return int.from_bytes(m.digest(), byteorder='big')
