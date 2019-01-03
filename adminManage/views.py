# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from adminManage import models

import json
import hashlib
import time
import uuid

def cb_passwordEqual(hash_value, salt, password):
    hash = hashlib.md5()
    hash.update(password + salt)
    return hash.hexdigest() == hash_value

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

    #    $userResult = array(
    #        'userId' => $adminInfo['user_id'],
    #        'userName' => $adminInfo['username'],
    #        'lastLoginTime' => $adminInfo['last_login_time'],
    #        'token' => array(
    #            'accessToken' => $adminInfo['access_token'],
    #            'tokenExpiresIn' => $adminInfo['token_expires_in'],
    #            'exp' => WEEK
    #        )
    #    );
    #    
    #    return success($userResult);
    #return HttpResponse("Hello, world. You're at the polls index.")

def get_qiniu_token(request):
    return HttpResponse("Hello, world. You're at the polls index.")
