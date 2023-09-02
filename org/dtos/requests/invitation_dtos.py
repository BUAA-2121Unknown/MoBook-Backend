# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 10:17
# @Author  : Tony Skywalker
# @File    : invitation_dtos.py
#


class BaseInvitationDto:
    def __init__(self):
        self.orgId: int = 0

    def is_valid(self):
        return True


class CreateInvitationDto(BaseInvitationDto):
    def __init__(self):
        super().__init__()
        self.expires: int = 0  # expire in day
        self.review: bool = False

    def is_valid(self):
        return self.expires > 0 or self.expires == -1


class RevokeInvitationDto(BaseInvitationDto):
    def __init__(self):
        super().__init__()
        self.id: int = 0


class ActivateInvSuccessData:
    """
    If review is true, then the user is not yet in the org.
    """

    def __init__(self, review: bool, profile, prev_in):
        self.review: bool = review
        self.profile = profile
        self.prevIn = prev_in
