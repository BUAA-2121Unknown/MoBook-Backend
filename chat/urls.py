"""
URL configuration for MoBook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from chat.views.chat_manage import create_chat, chat_invite_member, chat_remove_member, dismiss_chat, get_chat_members, \
    leave_chat, upload_chat_avatar
from chat.views.chat_messages import get_chat_list, get_all_messages, send_text, send_file, view_chat, \
    pull_older_messages, pull_newer_messages, get_messages_by_type, search_messages

urlpatterns = [
    path('index', get_chat_list, name='get_chat_list'),

    path('create', create_chat, name='create_chat'),
    path('upload_chat_avatar', upload_chat_avatar, name='upload_chat_avatar'),
    path('dismiss', dismiss_chat, name='chat_invite_member'),
    path('invite', chat_invite_member, name='chat_invite_member'),
    path('get_members', get_chat_members, name='get_chat_members'),
    path('remove', chat_remove_member, name='chat_remove_member'),
    path('leave', leave_chat, name='leave_chat'),

    path('get_all_messages', get_all_messages, name='get_all_messages'),
    path('view', view_chat, name='view_chat'),
    path('pull_old', pull_older_messages, name='pull_older_messages'),
    path('pull_new', pull_newer_messages, name='pull_newer_messages'),

    path('search_messages', search_messages, name='search_messages'),
    path('get_messages_by_type', get_messages_by_type, name='get_messages_by_type'),

    path('send_text', send_text, name='send_text'),
    path('send_file', send_file, name='send_file'),
]
