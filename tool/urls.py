# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/3/2023 2:46
# @Author  : Tony Skywalker
# @File    : urls.py
#
from django.urls import path

from tool.views import convert_html_to_docx

urlpatterns = [
    path('html2docx', convert_html_to_docx)
]
