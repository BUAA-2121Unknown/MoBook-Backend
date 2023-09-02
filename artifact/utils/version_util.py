# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/30/2023 20:27
# @Author  : Tony Skywalker
# @File    : version_util.py
#
from artifact.models import Item, FileVersion


def get_versions_of_file(file: Item):
    return FileVersion.objects.filter(file_id=file.id).order_by('-updated')
