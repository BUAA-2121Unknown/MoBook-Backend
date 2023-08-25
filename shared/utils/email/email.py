# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 9:55
# @Author  : Tony Skywalker
# @File    : email.py
#
from random import Random

from django.core.mail import EmailMessage
from django.template import loader

from MoBook.settings import EMAIL_FROM
from shared.utils.email.exception import EmailException


def generate_activation_code(length=6) -> str:
    code_character_set = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    code = ""
    max_idx = len(code_character_set) - 1
    random = Random()
    for i in range(length):
        code += code_character_set[random.randint(0, max_idx)]
    return code


def _send_email(title, template_name, email, dto: dict):
    template = loader.get_template("email/" + template_name)
    content = template.render(dto)

    msg = EmailMessage(title, content, EMAIL_FROM, [email])
    msg.content_subtype = 'html'
    try:
        send_status = msg.send()
        if not send_status:
            raise EmailException(send_status['errmsg'])
        print(send_status)
    except EmailException as e:
        raise e
    except Exception as e:
        raise EmailException(str(e))


def send_activation_email(email, link):
    _send_email(
            "MoBook Activation Email",
            "activation.html",
            email,
            {'link': link}
    )
