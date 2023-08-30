# Copyright (C) 2023 - 2023 Tony Skywalker. All Rights Reserved 
#
# @Time    : 8/26/2023 12:17
# @Author  : Tony Skywalker
# @File    : member.py
#
from chat.models import Chat
from chat.utils.assistance import add_users_to_chat, remove_users_from_chat
from org.models import Organization
from shared.utils.model.chat_extension import get_chats_of_organization
from shared.utils.model.model_extension import first_or_default
from shared.utils.model.organization_extension import get_org_profile_of_user
from shared.utils.model.project_extension import get_projects_of_organization
from user.models import User, UserOrganizationProfile, UserAuth


def add_member_into_org(org: Organization, user: User):
    """
    Each member added to the organization will be added to all
    its projects, for now
    """
    uop = get_org_profile_of_user(org, user)
    if uop is not None:
        return uop
    uop = UserOrganizationProfile.create(UserAuth.NORMAL, user, org)
    uop.save()

    # add member to projects
    # for project in get_projects_of_organization(org):
    #     add_users_to_project([user], project)

    # add member to default chat only
    chat = first_or_default(Chat, id=org.chat_id)
    if chat is not None:
        add_users_to_chat([user], chat)

    return uop


def kick_member_from_org(org: Organization, user: User, uop: UserOrganizationProfile):
    """
    Each member removed from the organization will be removed from all
    its projects, for now
    """
    uop.delete()

    # remove member from projects
    # for project in get_projects_of_organization(org):
    #     remove_users_from_project([user], project)

    # remove member from all chats
    for chat in get_chats_of_organization(org):
        remove_users_from_chat([user], chat)
