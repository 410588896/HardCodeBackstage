from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'login', views.login, name='login'),
    url(r'webConfig', views.get_web_config, name='get_web_config'),
]
