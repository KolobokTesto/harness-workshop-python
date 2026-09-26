import os


def load_settings():
    allow_digest_write = os.environ.get("APPROVED") == "1"
    return {"permissions": {"saveDigest": allow_digest_write}}
