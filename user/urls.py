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

from user.views.avatar import upload_avatar
from user.views.guide import get_user_guide
from user.views.org_record import update_last_organization, get_last_organization
from user.views.profile import update_user_profile, get_user_profile

urlpatterns = [
    path('avatar/upload', upload_avatar),
    path("profile/update", update_user_profile),
    path("profile", get_user_profile),
    path('lastorg/update', update_last_organization),
    path('lastorg/get', get_last_organization),
    path('guide', get_user_guide),
]
