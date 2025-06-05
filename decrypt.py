import base64
import hashlib

from Crypto.Cipher import AES

IV_CHECKSUM: int = 1398893684
KEY_CHECKSUM: int = 1701076831


def chunks(lst: bytes, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def words_to_bytes(words: list[int]) -> bytes:
    result = bytearray()

    for word in words:
        for i in range(4):
            byte_val = (word >> (24 - i * 8)) & 0xFF
            result.append(byte_val)

    return bytes(result)


def derive_key_iv(password: str, salt: list[int]) -> tuple[bytes, bytes, bytes]:
    hasher = hashlib.md5

    key_size_bytes = 32
    iv_size_bytes = 16
    total_needed = key_size_bytes + iv_size_bytes

    derived = b""
    prev_hash = b""

    salt_converted = words_to_bytes(salt)
    password_bytes = password.encode("utf-8")

    while len(derived) < total_needed:
        hash_input = prev_hash + password_bytes + salt_converted
        prev_hash = hasher(hash_input).digest()
        derived += prev_hash

    key = derived[:key_size_bytes]
    iv = derived[key_size_bytes : key_size_bytes + iv_size_bytes]
    return (key, iv, salt_converted)


def decrypt(encrypted: str, key: str) -> str:
    parsed = base64.b64decode(encrypted)
    words = [int.from_bytes(x, signed=True) for x in list(chunks(parsed, 4))]
    if words[0] == IV_CHECKSUM and words[1] == KEY_CHECKSUM:
        salt = words[2:4]
        cipher_text = words[4:]
        i = derive_key_iv(key, salt)
        m = AES.new(i[0], mode=AES.MODE_CBC, iv=i[1]).decrypt(  # pyright: ignore[reportUnknownMemberType]
            words_to_bytes(cipher_text)
        )
        return m.decode("utf-8")
    return ""
