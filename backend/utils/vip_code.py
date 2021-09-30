import hashlib

import secrets

code_show = "abcdefghjklmnopqrstuvwxyz" + "abcdefghjklmnopqrstuvwxyz".upper()


def generate_by_username(username: str, length: int = 6) -> str:
    code = int(hashlib.md5(f"username: {username}, slat: {secrets.SECRET_VIP_CODE_SALT}".encode()).hexdigest(), 16)
    vip_code = ''
    while length > 0:
        vip_code += code_show[code % len(code_show)]
        code = code // len(code_show)
        length -= 1
    return vip_code


def vip_code_check(vip_code: int, username: str) -> bool:
    vip_code_sample = generate_by_username(username)
    return vip_code == vip_code_sample
