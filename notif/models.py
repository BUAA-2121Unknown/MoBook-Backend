from django.db import models

from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from shared.utils.json.serializer import serialize
from user.models import UserAuth


class NotifType:
    UNKNOWN = 0
    TEXT = 1
    AT = 2
    INVITATION = 3
    ROLE_CHANGE = 4
    KICKED = 5


class NotifBasePayload:
    def __init__(self, type: int, text: str):
        self.type: int = type
        self.text: str = text


class NotifTextPayload(NotifBasePayload):
    def __init__(self, text: str):
        super().__init__(NotifType.TEXT, text)


class NotifAtPayload(NotifBasePayload):
    def __init__(self, text: str, org_id: int, chat_id: int, msg_id: int):
        super().__init__(NotifType.AT, text)
        self.orgId = org_id
        self.chatId = chat_id
        self.msgId = msg_id


class NotifInvitationPayload(NotifBasePayload):
    def __init__(self, text: str, status: int, org: Organization):
        super().__init__(NotifType.INVITATION, text)
        self.status: int = status  # 0 rejected, 1 accepted
        self.org: OrganizationDto = OrganizationDto(org)


class NotifRoleChangePayload(NotifBasePayload):
    def __init__(self, text: str, org: Organization, new_auth: int):
        super().__init__(NotifType.ROLE_CHANGE, text)
        self.newAuth: str = UserAuth.to_string(new_auth)
        self.org: OrganizationDto = OrganizationDto(org)


class NotifKickedPayload(NotifBasePayload):
    def __init__(self, text: str, org: Organization):
        super().__init__(NotifType.KICKED, text)
        self.org: OrganizationDto = OrganizationDto(org)


class NotifStatus:
    UNREAD = 0
    READ = 1
    DELETED = 2

    @classmethod
    def all(cls):
        return [cls.UNREAD, cls.READ, cls.DELETED]


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
