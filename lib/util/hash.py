import hashlib
import base64
from datetime import datetime

def sha256(msg) -> str:
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

def generage_random_hash() -> str:
    return base64.b32encode(
        hashlib.sha256(
            (
                'random_words' + str(datetime.now())
            ).encode('utf-8')
        ).digest()
    ).decode('utf-8')