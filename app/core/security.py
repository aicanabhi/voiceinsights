import bcrypt

# bcrypt only reads the first 72 bytes of a password and raises on anything
# longer, so inputs are truncated here rather than at the call sites.
BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        _encode(password),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    try:
        return bcrypt.checkpw(
            _encode(plain_password),
            hashed_password.encode("utf-8")
        )

    except ValueError:
        # malformed or non-bcrypt hash stored for this user
        return False
