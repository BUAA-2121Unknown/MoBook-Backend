from django.db import models

from chat.dtos.chat_dto import ChatDto
from chat.models import Chat
from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from project.dtos.models.project_dto import ProjectDto
from project.models import Project
from shared.utils.json.serializer import serialize
from user.dtos.user_dto import UserDto
from user.models import UserAuth, User


class NotifType:
    UNKNOWN = 0
    TEXT = 1
    AT = 2
    INVITATION = 3
    ROLE_CHANGE = 4
    KICKED = 5
    NEW_PROJECT = 6


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
    def __init__(self, text: str, status: int, org: Organization):
        super().__init__(NotifType.INVITATION, text)
        self.status: int = status  # 0 rejected, 1 accepted
        self.org: OrganizationDto = OrganizationDto(org)


class NotifRoleChangePayload(NotifBasePayload):
    """
    your role in {organization} changed to {new_auth}
    """
    def __init__(self, text: str, org: Organization, new_auth: int):
        super().__init__(NotifType.ROLE_CHANGE, org)
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


class NotifStatus:
    UNREAD = 0
    READ = 1
    DELETED = 2

    @classmethod
    def all(cls):
        return [cls.UNREAD, cls.READ, cls.DELETED]

    @classmethod
    def valid(cls):
        return [cls.UNREAD, cls.READ]


class Notification(models.Model):
    user_id = models.BigIntegerField(default=0)  # target user
    org_id = models.BigIntegerField(default=0)  # belonging org

    type = models.SmallIntegerField(default=0)
    payload = models.TextField(default="{}")

    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    status = models.SmallIntegerField(default=NotifStatus.UNREAD)

    @classmethod
    def create(cls, user_id, org_id, payload):
        try:
            typ = payload.type
            pl = serialize(payload)
        except Exception:
            return None
        return cls(user_id=user_id, org_id=org_id, type=typ, payload=pl)

    class Meta:
        managed = True
        db_table = 'Notification'
