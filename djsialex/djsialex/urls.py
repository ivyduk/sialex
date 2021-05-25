"""djsialex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
import os

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views


from administracion.forms import UserAuthenticationWithCaptchaForm
from djsialex import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administracion.urls')),
    url(r'^acceso/login/$', auth_views.LoginView.as_view(template_name=os.path.join(settings.TEMPLATE_DIR, 'registration/login.html'),
                        authentication_form=UserAuthenticationWithCaptchaForm), name='login'),
    url(r'^acceso/', include('django.contrib.auth.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^markdownx/', include('markdownx.urls')),

]

admin.site.site_header = 'Administración de Sialex'
admin.site.site_title = "SIALEX"
admin.site.index_title = "Módulo de Administración"