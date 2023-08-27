from chat.models import Chat
from user.models import UserChatRelation


def create_chat(org_id, chat_name, user_id):

    chat = Chat(org_id=org_id, type=1, chat_name=chat_name)
    chat.save()

    # 拉创始人
    user_chat_relation = UserChatRelation(user_id=user_id, chat_id=chat.id, authority=1)
    user_chat_relation.save()

    return 0


def add_to_chat(chat_id, user_list):

    for user in user_list:
        user_chat_relation = UserChatRelation(user_id=user.id, chat_id=chat_id, authority=1)
        user_chat_relation.save()

    return 0
