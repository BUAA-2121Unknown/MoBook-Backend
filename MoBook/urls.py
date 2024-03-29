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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from MoBook.settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/oauth/', include(('oauth.urls', 'oauth'))),
                  path('api/chat/', include(('chat.urls', 'chat'))),
                  path('api/user/', include(('user.urls', 'user'))),
                  path('api/org/', include(('org.urls', 'org'))),
                  path('api/proj/', include(('project.urls', 'project'))),
                  path('api/notif/', include(('notif.urls', 'notif'))),
                  path('api/live/', include(('live.urls', 'live'))),
                  path('api/artifact/', include(('artifact.urls', 'artifact'))),
                  path('api/tool/', include(('tool.urls', 'tool')))
              ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
