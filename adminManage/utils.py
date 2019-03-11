# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from adminManage import models

import hashlib
import re
import time
from random import Random

def is_p_number(num):
    try:
        z=int(num)
        return isinstance(z,int)
    except ValueError:
        return False

def cb_passwordEqual(hash_value, salt, password):
    hash = hashlib.md5()
    hash.update(password + salt)
    return hash.hexdigest() == hash_value

def create_salt(length = 4):
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    #获取chars的最大下标
    len_chars = len(chars)-1
    random = Random()
    for i in range(length):
        #每次随机从chars中抽取一位,拼接成一个salt值
        salt += chars[random.randint(0,len_chars)]
    return salt

def cb_encrypt(password): 
    #salt = password_hash('mypassword', 1, {'cost':10})
    salt = create_salt()
    hash = hashlib.md5()
    hash.update(password + salt)
    password = hash.hexdigest()
    return {
            'password': password,
            'salt': salt,
        }

def check_token(request):
    accessToken = request.META.get('accessToken', '')
    #检查token是否存在并且是否有效
    num = models.Admin.objects.filter(access_token=accessToken).count()
    if num == 0:
        return False
    userInfo = models.Admin.objects.get(access_token=accessToken)
    if userInfo.token_expires_in < int(time.time()):
        return False

    #查得到数据并且token在效期内
    return True

def get_ip(request):
    ip = ''
    if request.META.get('HTTP_CLIENT_IP', 'unknow') != 'unknow':
        ip = request.META.get('HTTP_CLIENT_IP', 'unknow')
    elif request.META.get('HTTP_X_FORWARDED_FOR', 'unknow') != 'unknow':
        ip = request.META.get('HTTP_X_FORWARDED_FOR', 'unknow')
    elif request.META.get('REMOTE_ADDR', 'unknow') != 'unknow':
        ip = request.META.get('REMOTE_ADDR', 'unknow')
    elif request.POST.get('REMOTE_ADDR', 'unknow') != 'unknow':
        ip = request.POST.get('REMOTE_ADDR', 'unknow')
    elif request.GET.get('REMOTE_ADDR', 'unknow') != 'unknow':
        ip = request.GET.get('REMOTE_ADDR', 'unknow')

    ip = re.match('/[\d\.]{7,15}/', ip)
    if ip is None:
        ip = ''
    return ip

def save_sys_log(message, request):
    data = {
        'time': int(time.time()),
        'content': message,
        'ip': get_ip(request),
    }
    models.SysLog.objects.create(data)

def dictfetchall(cursor): 
    '''Returns all rows from a cursor as a dict'''
    desc = cursor.description 
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] 

def get_page(params, maxPageSize = 99, defaultPageSize = 15):
    page = dict()
    page['page'] = params.get('page', '')
    page['pageSize'] = params.get('pageSize', '')
    if is_p_number(page['page']) == False:
        page['page'] = '0'
    if is_p_number(page['pageSize']) == False or int(page['pageSize']) > defaultPageSize:
        page['pageSize'] = defaultPageSize
    return page 

def get_param(params, key, default = ''):
    param = default
    if params.has_key(key):
        param = params[key]
    return param

