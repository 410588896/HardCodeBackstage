# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Admin(models.Model):
    aid = models.AutoField(primary_key=True)
    user_id = models.CharField(unique=True, max_length=128)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires_in = models.IntegerField(blank=True, null=True)
    create_time = models.IntegerField()
    status = models.TextField()  # This field type is a guess.
    last_login_time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin'
        unique_together = (('aid', 'user_id'),)


class Article(models.Model):
    aid = models.AutoField(primary_key=True)
    id = models.CharField(unique=True, max_length=128)
    title = models.CharField(max_length=255, blank=True, null=True)
    category_id = models.CharField(max_length=128, blank=True, null=True)
    create_time = models.IntegerField()
    delete_time = models.IntegerField(blank=True, null=True)
    update_time = models.IntegerField(blank=True, null=True)
    publish_time = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    cover = models.TextField(blank=True, null=True)
    sub_message = models.TextField(blank=True, null=True)
    pageview = models.IntegerField(blank=True, null=True)
    is_encrypt = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'article'
        unique_together = (('aid', 'id'),)


class ArticleTagMapper(models.Model):
    article_id = models.CharField(max_length=128)
    tag_id = models.CharField(max_length=128)
    create_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'article_tag_mapper'


class BlogConfig(models.Model):
    blog_name = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.TextField(blank=True, null=True)
    sign = models.TextField(blank=True, null=True)
    wxpay_qrcode = models.TextField(blank=True, null=True)
    alipay_qrcode = models.TextField(blank=True, null=True)
    github = models.TextField(blank=True, null=True)
    view_password = models.CharField(max_length=255, blank=True, null=True)
    salt = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blog_config'


class Category(models.Model):
    aid = models.AutoField(primary_key=True)
    id = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.IntegerField()
    update_time = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    article_count = models.IntegerField(blank=True, null=True)
    can_del = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'category'
        unique_together = (('aid', 'id'),)


class Comments(models.Model):
    article_id = models.CharField(max_length=128)
    parent_id = models.IntegerField()
    reply_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=128, blank=True, null=True)
    content = models.TextField()
    source_content = models.TextField(blank=True, null=True)
    create_time = models.IntegerField()
    delete_time = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    is_author = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'comments'


class Friends(models.Model):
    aid = models.AutoField(primary_key=True)
    friend_id = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=255)
    url = models.TextField()
    create_time = models.IntegerField()
    update_time = models.IntegerField(blank=True, null=True)
    delete_time = models.IntegerField(blank=True, null=True)
    status = models.TextField()  # This field type is a guess.
    type_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'friends'
        unique_together = (('aid', 'friend_id'),)


class FriendsType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friends_type'


class Pages(models.Model):
    type = models.CharField(max_length=128)
    md = models.TextField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pages'


class SysLog(models.Model):
    time = models.IntegerField()
    content = models.TextField(blank=True, null=True)
    ip = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sys_log'


class Tag(models.Model):
    aid = models.AutoField(primary_key=True)
    id = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.IntegerField()
    update_time = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    article_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tag'
        unique_together = (('aid', 'id'),)
