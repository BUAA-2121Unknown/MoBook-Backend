# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 9/3/2023 2:53
# @Author  : Tony Skywalker
# @File    : docx_util.py
#
import uuid

from docx import Document
from htmldocx import HtmlToDocx

from MoBook.settings import BASE_URL
from shared.utils.dir_utils import ensure_file_parent_path
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import construct_file_response_raw


def _generate_docx_path(filename):
    core_path = f"{uuid.uuid4().hex}/{filename}.docx"
    return f"./media/docx/{core_path}", f"{BASE_URL}/media/docx/{core_path}"


def prepare_docx_file(html, filename):
    try:
        document = Document()
        new_parser = HtmlToDocx()
        new_parser.add_html_to_document(html, document)
        path, url = _generate_docx_path(filename)
        ensure_file_parent_path(path)
        document.save(path)
    except Exception as e:
        raise FileException("Failed to generate DOCX file: " + str(e)) from e

    return url


def construct_docx_file_response(file, filename):
    return construct_file_response_raw(file,
                                       filename,
                                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
