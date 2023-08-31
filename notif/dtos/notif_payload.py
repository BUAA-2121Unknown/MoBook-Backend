# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/27/2023 23:14
# @Author  : Tony Skywalker
# @File    : notif_payload.py
#
from artifact.dtos.models.item_dto import FileDto
from artifact.models import Item
from chat.dtos.chat_dto import ChatDto
from chat.models import Chat
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.dtos.models.project_dto import ProjectDto
from project.models import Project
from user.dtos.user_dto import UserDto
from user.models import User, UserAuth


class NotifType:
    UNKNOWN = 0
    TEXT = 1
    AT = 2
    INVITATION = 3
    ROLE_CHANGE = 4
    KICKED = 5
    NEW_PROJECT = 6
    ARTIFACT_AT = 7


class NotifBasePayload:
    def __init__(self, typ: int, org: Organization):
        self.type: int = typ
        self.org = OrganizationDto(org)


class NotifTextPayload(NotifBasePayload):
    """
    system send you a text notification
    """

    def __init__(self, org: Organization, text: str):
        super().__init__(NotifType.TEXT, org)
        self.text: str = text


class NotifAtPayload(NotifBasePayload):
    """
    {someone} at you in {chat}
    """

    def __init__(self, org: Organization, user: User, chat: Chat):
        super().__init__(NotifType.AT, org)
        self.user: UserDto = UserDto(user)
        self.chat: ChatDto = ChatDto(chat)


class NotifInvitationPayload(NotifBasePayload):
    """
    On hold
    """

    def __init__(self, status: int, org: Organization):
        super().__init__(NotifType.INVITATION, org)
        self.status: int = status  # 0 rejected, 1 accepted
        self.org: OrganizationDto = OrganizationDto(org)


class NotifRoleChangePayload(NotifBasePayload):
    """
    your role in {organization} changed from {old_auth} to {new_auth}
    """

    def __init__(self, org: Organization, old_auth: int, new_auth: int):
        super().__init__(NotifType.ROLE_CHANGE, org)
        self.oldAuth: str = UserAuth.to_string(old_auth)
        self.newAuth: str = UserAuth.to_string(new_auth)


class NotifKickedPayload(NotifBasePayload):
    def __init__(self, org: Organization):
        super().__init__(NotifType.KICKED, org)


class NotifNewProjectPayload(NotifBasePayload):
    """
    {someone} created a {new project} in {organization}
    """

    def __init__(self, org: Organization, user: User, project: Project):
        super().__init__(NotifType.NEW_PROJECT, org)
        self.user: UserDto = UserDto(user)
        self.project: ProjectDto = ProjectDto(project)


class NotifFileAtPayload(NotifBasePayload):
    """
    {someone} at you in {artifact}
    """

    def __init__(self, org: Organization, target_user: User, proj: Project, file: Item):
        super().__init__(NotifType.ARTIFACT_AT, org)
        self.user: UserDto = UserDto(target_user)
        self.project: ProjectDto = ProjectDto(proj)
        self.artifact: FileDto = FileDto(art)
