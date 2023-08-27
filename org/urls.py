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

from org.views.avatar import upload_org_avatar
from org.views.invitation import create_invitation, revoke_invitation, activate_invitation, get_invitation_of_org, \
    get_preview_of_invitation
from org.views.manage import create_org, cancel_org
from org.views.member import update_org_member_profile, get_members_of_org, kick_member
from org.views.pending import user_update_pending, admin_update_pending
from org.views.profile import update_org_profile, get_org_profile
from org.views.project import get_projects_of_org

urlpatterns = [
    path('avatar/upload', upload_org_avatar),

    path('create', create_org),
    path('cancel', cancel_org),

    path('profile/update', update_org_profile),
    path('profile', get_org_profile),

    path('member/profile/update', update_org_member_profile),
    # path('member/profile', get_org_member_profile),
    path('members', get_members_of_org),

    path('member/auth/invite', create_invitation),
    path('member/auth/revoke', revoke_invitation),
    path('member/auth/activate', activate_invitation),
    path('member/auth/kick', kick_member),

    path('member/auth/preview', get_invitation_of_org),
    path('member/auth/invitations', get_preview_of_invitation),

    path('member/auth/pending/user/update', user_update_pending),
    # path('member/auth/pending/user', user_get_pending),
    path('member/auth/pending/admin/update', admin_update_pending),
    # path('member/auth/pending/admin', admin_get_pending),

    path('projects', get_projects_of_org),
]
