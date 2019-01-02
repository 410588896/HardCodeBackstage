from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'login', views.login, name='login'),
    url(r'qiniu/token', views.get_qiniu_token, name='get_qiniu_token'),
]
