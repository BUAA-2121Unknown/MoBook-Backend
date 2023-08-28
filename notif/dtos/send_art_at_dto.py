# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/28/2023 10:53
# @Author  : Tony Skywalker
# @File    : send_art_at_dto.py
#
from typing import List


class SendArtAtNotifDto:
    """
    {sender} in {artifact} of {project} send at message to {[ users ]}
    """

    def __init__(self):
        self.projId: int = 0
        self.artId: int = 0
        self.users: List[int] = [0]
