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
    url(r'friends/add', views.add_friend, name='add_friend'),
    url(r'friends/modify', views.modify_friend, name='modify_friend'),
    url(r'friends/delete', views.del_friend, name='del_friend'),
    url(r'category/add', views.add_category, name='add_category'),
    url(r'category/modify', views.modify_category, name='modify_category'),
    url(r'category/delete', views.del_category, name='del_category'),
    url(r'category/list', views.get_category_list, name='get_category_list'),
    url(r'category', views.get_category, name='get_category'),
    url(r'tag/add', views.add_tag, name='add_tag'),
    url(r'tag/modify', views.modify_tag, name='modify_tag'),
]
