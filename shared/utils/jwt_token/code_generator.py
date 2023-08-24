# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/24/2023 23:11
# @Author  : Tony Skywalker
# @File    : code_generator.py
#
from random import Random

CODE_CHARACTER_SET = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789~!@#$%^&*()-+=[]{}|:;<>,.?'


def generate_code(length=6) -> str:
    code = ""
    max_idx = len(CODE_CHARACTER_SET) - 1
    random = Random()
    for i in range(length):
        code += CODE_CHARACTER_SET[random.randint(0, max_idx)]
    return code
