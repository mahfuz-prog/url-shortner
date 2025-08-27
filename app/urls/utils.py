import string

"""
Digits: 0-9
Lowercase letters: a-z
Uppercase letters: A-Z

62^10 combination in 10 chars
"""
BASE62 = string.digits + string.ascii_letters


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62[0]
    arr = []
    base = len(BASE62)
    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62[rem])
    arr.reverse()
    return "".join(arr)


def decode_base62(s: str) -> int:
    num = 0
    base = len(BASE62)
    for c in s:
        num = num * base + BASE62.index(c)
    return num
