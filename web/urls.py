from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'getAbout', views.get_about_me, name='get_about_me'),
    url(r'getResume', views.get_resume, name='get_resume'),
    url(r'blogInfo', views.get_blog_info, name='get_blog_info'),
]
