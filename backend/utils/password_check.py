# 规则：至少8位，包含数字和字母

def password_check(password: str) -> tuple:
    # has_numbers = False
    # has_letters = False
    # result_text = []
    #
    # for c in password:
    #     if '0' <= c <= '9':
    #         has_numbers = True
    #     if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
    #         has_letters = True
    # if len(password) < 8:
    #     result_text.append("密码必须长于8位")
    # if not has_letters:
    #     result_text.append('必须包含英文字母')
    # if not has_numbers:
    #     result_text.append('必须包含数字字符')
    # if len(result_text) == 0:
    #     return True, 'OK'
    # return False, '；'.join(result_text) + '。'
    return True, 'OK'
