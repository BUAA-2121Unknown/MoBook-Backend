# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/25/2023 10:03
# @Author  : Tony Skywalker
# @File    : send_email_task.py
#
from celery import shared_task
from celery.utils.time import timezone

from oauth.models import EmailRecord
from shared.utils.email.email import generate_activation_code, send_activation_email
from shared.utils.email.exception import EmailException


@shared_task
def send_activation_email_task(email, link):
    code = generate_activation_code()
    link += "?code=" + code
    print(link)
    try:
        send_activation_email(email, link)
    except EmailException as e:
        return
    print(email)
    # delete previous emails
    for email in EmailRecord.objects.filter(email=email, usage="activation", valid=True):
        email.valid = False
        email.save()
    expire = timezone.now() + timezone.timedelta(minutes=10)
    email = EmailRecord.create(email, code, expire, "activation")
    email.save()
