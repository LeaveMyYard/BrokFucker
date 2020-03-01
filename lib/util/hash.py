import hashlib

def sha256(msg) -> str:
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()