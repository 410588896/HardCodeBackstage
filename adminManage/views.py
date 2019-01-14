# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from django.db import connection

from adminManage import models

from utils import *

import json
import time
import uuid


def login(request):
    ret = dict()
    if request.method == 'POST':
        #检查用户名是否存在
        parm = request.POST
        username_value = parm.get('username','not found')
        isEx = models.Admin.objects.filter(username=username_value).count()
        if isEx == 0:
    	    ret["status"] = False
    	    ret["code"] = -1
    	    ret["msg"] = '该账号不存在'
    	    ret['data'] = []
            return HttpResponse(json.dumps(ret))
        #查询账号信息
        userinfo = models.Admin.objects.get(username=username_value)
        if ord(userinfo.status) != 0:
    	    ret["status"] = False
    	    ret["code"] = -1
    	    ret["msg"] = '账号异常'
    	    ret['data'] = []
            return HttpResponse(json.dumps(ret))
        #比对密码
        if cb_passwordEqual(userinfo.password, userinfo.salt, parm.get('password','not found')) == False:
    	    ret["status"] = False
    	    ret["code"] = -1
    	    ret["msg"] = '密码错误'
    	    ret['data'] = []
            return HttpResponse(json.dumps(ret))
        #更新登陆时间
        cur_time = int(time.time())
        access_token = str(uuid.uuid1())
        data = {
            "last_login_time": cur_time,
            "access_token": str(uuid.uuid1()),
            "token_expires_in": cur_time + 60 * 60 * 24 * 7,
        }
        #更新数据
        models.Admin.objects.filter(username=username_value).update(**data)

        userinfo = models.Admin.objects.get(username=username_value)
        retdata = {
            "userId": userinfo.user_id,
            "userName": userinfo.username,
            "lastLoginTime": userinfo.last_login_time,
            "token": {
                         "accessToken": userinfo.access_token,
                         "tokenExpiresIn": userinfo.token_expires_in,
                         "exp": 60 * 60 * 24 * 7, 
            },
        }
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '登陆成功'
    	ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
    else:
    	ret["status"] = False
    	ret["code"] = -1
    	ret["msg"] = '该账号不存在'
    	ret['data'] = []
        return HttpResponse(json.dumps(ret))

def get_web_config(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    config = models.BlogConfig.objects.values_list('blog_name', 'avatar', 'sign', 'wxpay_qrcode', 'alipay_qrcode', 'github', 'salt')
    retdata = dict()
    if len(config) != 0 and config[0][6] != "NULL":
        retdata['blogName'] = config[0][0]
        retdata['avatar'] = config[0][1]
        retdata['sign'] = config[0][2]
        retdata['wxpayQrcode'] = config[0][3]
        retdata['alipayQrcode'] = config[0][4]
        retdata['github'] = config[0][5]
        retdata['hadOldPassword'] = True
	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
    else:
        retdata['blogName'] = config[0][0]
        retdata['avatar'] = config[0][1]
        retdata['sign'] = config[0][2]
        retdata['wxpayQrcode'] = config[0][3]
        retdata['alipayQrcode'] = config[0][4]
        retdata['github'] = config[0][5]
        retdata['hadOldPassword'] = False
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
    if len(config) == 0:
    	ret["status"] = False
    	ret["code"] = -1
    	ret["msg"] = '查询失败'
    	ret['data'] = []
    return HttpResponse(json.dumps(ret))
	
def modify(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    config_len = models.BlogConfig.objects.count()
    #查询到数据库中信息
    if 0 != config_len:
        config = models.BlogConfig.objects.all()[:1]
        parm = request.POST
        if 'true' == parm.get('settingPassword','not found'):
            #如果有秘钥存在，说明已经有设置过密码了，要对密码进行比较
            if config.salt != 'NULL':
                if cb_passwordEqual(config.view_password, config.salt, parm.get('oldPassword','not found')) == False:
    	            ret["status"] = False
    	            ret["code"] = -1
    	            ret["msg"] = '原密码错误'
    	            ret['data'] = []
                    return HttpResponse(json.dumps(ret))
            #加密新密码
            encrypt = cb_encrypt(parm.get('viewPassword', 'not found'))
            config.view_password = encrypt['password']
            config.salt = encrypt['salt']

        config.blog_name = parm.get('blogName', 'not found')
        config.avatar = parm.get('avatar', 'not found')
        config.sign = parm.get('sign', 'not found')
        config.wxpay_qrcode = parm.get('wxpayQrcode', 'not found')
        config.alipay_qrcode = parm.get('alipayQrcode', 'not found')
        config.github = parm.get('github', 'not found')
        save_config = models.BlogConfig.objects.get(id=config.id)
        save_config = config
        save_config.save()
    else:
        config = dict()
        if parm.get('settingPassword', 'not found') == 'true':
            #加密新密码
            encrypt = cb_encrypt(parm.get('viewPassword', 'not found'))
            config['view_password'] = encrypt['password']
            config['salt'] = encrypt['salt']
        config['blog_name'] = parm.get('blogName', 'not found')
        config['avatar'] = parm.get('avatar', 'not found')
        config['sign'] = parm.get('sign', 'not found')
        config['wxpay_qrcode'] = parm.get('wxpayQrcode', 'not found')
        config['alipay_qrcode'] = parm.get('alipayQrcode', 'not found')
        config['github'] = parm.get('github', 'not found')
        
        models.BlogConfig.objects.create(**config)
        
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '更新成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def get_about_me(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    isEX = models.Pages.objects().filter(type='about').count()
    if isEX == 0:
        ret["status"] = True
        ret["code"] = 0
        ret["msg"] = '未找到关于我页面'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
        
    config = models.Pages.objects().get(type='about')
    retdata = dict()
    if config.md == 'null':
        retdata['md'] = ''
        retdata['type'] = config.type
        retdata['html'] = config.html

    if config.html == 'null':
        retdata['html'] = ''
        retdata['type'] = config.type
        retdata['md'] = config.md

    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '查询成功'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))

def modify_about(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    isEX = models.Pages.objects().filter(type='about').count()
    parm = request.GET
    if isEX != 0:
        config = models.Pages.objects().get(type='about')
        models.Pages.objects.filter(id=config.id).update(**{'md': parm.get('content', 'null'), 'html': parm.get('htmlContent', 'null')})
    else:
        models.Pages.objects.create(**{'md': parm.get('content', 'null'), 'html': parm.get('htmlContent', 'null'), 'type': 'about'})
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '更新成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def get_resume(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    isEX = models.Pages.objects().filter(type='resume').count()
    if isEX == 0:
        ret["status"] = True
        ret["code"] = 0
        ret["msg"] = '未找到简历页面'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
        
    config = models.Pages.objects().get(type='resume')
    retdata = dict()
    if config.md == 'null':
        retdata['md'] = ''
        retdata['type'] = config.type
        retdata['html'] = config.html

    if config.html == 'null':
        retdata['html'] = ''
        retdata['type'] = config.type
        retdata['md'] = config.md

    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '查询成功'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))

def modify_resume(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    isEX = models.Pages.objects().filter(type='resume').count()
    parm = request.GET
    if isEX != 0:
        config = models.Pages.objects().get(type='resume')
        models.Pages.objects.filter(id=config.id).update(**{'md': parm.get('content', 'null'), 'html': parm.get('htmlContent', 'null')})
    else:
        models.Pages.objects.create(**{'md': parm.get('content', 'null'), 'html': parm.get('htmlContent', 'null'), 'type': 'about'})
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '更新成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def get_friends_type(request):
    ret = dict()
    if check_token(request) == False:
	ret["status"] = False
    	ret["code"] = -4001
    	ret["msg"] = '无效的token'
    	ret['data'] = []
    cursor = connection.cursor()
    cursor.execute("select name,count from friends_type order by id desc")
    typeList = dictfetchall(cursor)
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = 'success'
    ret['data'] = typeList
    return HttpResponse(json.dumps(ret))

