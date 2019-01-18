from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'login', views.login, name='login'),
    url(r'webConfig', views.get_web_config, name='get_web_config'),
    url(r'webConfig/modify', views.modify, name='modify'),
    url(r'webConfig/modifyAbout', views.modify_about, name='modify_about'),
    url(r'webConfig/getAbout', views.get_about_me, name='get_about_me'),
    url(r'webConfig/modifyAbout', views.modify_about, name='modify_about'),
    url(r'webConfig/getResume', views.get_resume, name='get_resume'),
    url(r'webConfig/modifyResume', views.modify_resume, name='modify_resume'),
    url(r'friends/typeList', views.get_friends_type, name='get_friends_type'),
    url(r'friends/list', views.get_friends_list, name='get_friends_list'),
]
