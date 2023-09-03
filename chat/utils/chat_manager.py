from chat.models import Chat, ChatType
from shared.utils.dir_utils import get_avatar_url
from shared.utils.model.model_extension import first_or_default
from user.models import UserChatRelation, User, UserOrganizationProfile, ChatAuth


def create_chat(org_id, chat_name, user_id):
    chat = Chat(org_id=org_id, type=1, chat_name=chat_name)
    chat.save()

    # 拉创始人
    user_chat_relation = UserChatRelation(user_id=user_id, chat_id=chat.id, authority=1, org_id=org_id)
    user_chat_relation.save()
    return chat


def add_to_chat(org_id, chat_id, user_id, authority):
    user_chat_relation = UserChatRelation(user_id=user_id, chat_id=chat_id, authority=authority, org_id=org_id)
    user_chat_relation.save()


def remove_from_chat(chat_id, user_list):
    chat = first_or_default(Chat, id=chat_id)
    # if chat is None
    if chat.type == 0:
        UserChatRelation.objects.filter(chat_id=chat_id).delete()
        chat.delete()
    else:
        for user in user_list:
            user_chat_relation = UserChatRelation.objects.filter(user_id=user.id, chat_id=chat_id)
            user_chat_relation.delete()


def _get_chat_members(chat_id, org_id, user_id):
    data = {"users": []}
    chat = first_or_default(Chat, id=chat_id)
    # print(org_id)
    tmp = []
    for user_chat_relation in UserChatRelation.objects.filter(chat_id=chat_id, org_id=org_id):

        user = first_or_default(User, id=user_chat_relation.user_id)
# <<<<<<< HEAD
#         data["users"].append({
#             "_id": str(user.id),
#             "username": first_or_default(UserOrganizationProfile, user_id=user.id,
#                                          org_id=org_id).nickname,
#             "avatar": get_avatar_url("user", user.avatar),
# =======
#         if chat.type == ChatType.ORG:
        #     if first_or_default(UserOrganizationProfile, user_id=user.id,
        #                                      org_id=org_id).auth == 2:
        #         auth = 0
        #     else:
        #         auth = 1
        #     tmp.append({
        #         "_id": str(user.id),
        #         "username": first_or_default(UserOrganizationProfile, user_id=user.id,
        #                                      org_id=org_id).nickname,
        #         "avatar": get_avatar_url("user", user.avatar),
        #         "auth": auth
        #     })
        # else:
        tmp.append({
            "_id": str(user.id),
            "username": first_or_default(UserOrganizationProfile, user_id=user.id,
                                         org_id=org_id).nickname,
            "avatar": get_avatar_url("user", user.avatar),
            "auth": user_chat_relation.authority
        })
    # if first_or_default(UserChatRelation, user_id=user_id, org_id=org_id, chat_id=chat_id).authority == ChatAuth.ADMIN:
    tmp.append({
        "_id": str(0),
        "username": "所有人",
        "avatar": "",
# >>>>>>> zdw
        })

    tmp = sorted(tmp, key=lambda x: int(x["_id"]))
    data["users"] = tmp



    return data
