import time
import secrets
import hashlib


def random_id() -> str:

    ts: int = int(time.time() * 1_000_000) & ((1 << 48) - 1)
    rand: int = secrets.randbits(32)

    data: bytes = ts.to_bytes(6, "big") + rand.to_bytes(4, "big")
    digest: bytes = hashlib.sha256(data).digest()[:16]

    return digest.hex()