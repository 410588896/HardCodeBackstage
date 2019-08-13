# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from django.db import connection

from django.db.models import Q

from adminManage import models

from adminManage.utils import *

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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
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
        return HttpResponse(json.dumps(ret))
    cursor = connection.cursor()
    cursor.execute("select name,count from friends_type order by id desc")
    typeList = dictfetchall(cursor)
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = 'success'
    ret['data'] = typeList
    return HttpResponse(json.dumps(ret))

def get_friends_list(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    pageOpt = get_page(parm)
    cursor = connection.cursor()
    cursor.execute("select friend_id as friendId, friends.name, url, create_time as createTime, update_time as updateTime,delete_time as deleteTime, friends.status as status, friends_type.name as typeName, type_id as typeId from friends join friends_type on friends.type_id = friends_type.id")
    friendsList = dictfetchall(cursor)
    retdata = {
        'page': pageOpt['page'],
        'pageSize': pageOpt['pageSize'],
        'count': len(friendsList),
        'list': friendsList,
    }
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = 'success'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))

def add_friend(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    data = {
        'name': '',
        'url': '',
        'typeId': '',
        'typeName': '',
    }

    for item in data:
        data[item] = get_param(parm, item) 
    if data['name'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['url'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '链接不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['typeId'] == '' and data['typeName'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '类型不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
   
    if data['typeId'] == '': 
        #如果类型id为空，说明是新增的类型，先添加进类型表
        isEx = models.FriendsType.objects.filter(name=data['typeName']).count()
        id = ''
        if isEx != 0:
            #如果已经存在这个类型名，就直接返回id
            typedata = models.FriendsType.objects.get(name=data['typeName'])
            id = typedata.id
        else:
            typeinfo = {
                'name': data['typeName'],
                'count': 1,
            }
            models.FriendsType.objects.create(typeinfo)
            typedata = models.FriendsType.objects.get(name=data['typeName'])
            id = typedata.id
        data['typeId'] = id

    friend = {
        'friend_id': str(uuid.uuid1()),
        'name': data['name'],
        'url': data['url'],
        'type_id': data['typeId'],
        'create_time': int(time.time()),
    }
    typeinfo = models.FriendsType.objects.get(id=data['typeId'])
    typeCount = typeinfo.count + 1

    models.FriendsType.objects.filter(id=data['typeId']).update(count=typeCount)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '添加成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def modify_friend(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    data = {
        'friendId': '',
        'name': '',
        'url': '',
        'typeId': '',
        'typeName': '',
    }
    for item in data:
        data[item] = get_param(parm, item) 
    if data['friendId'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['name'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['url'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '链接不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['typeId'] == '' and data['typeName'] == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '类型不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Friends.filter(friend_id=data['friendId']).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['typeId'] == '':
        #如果类型id为空，说明是新增的类型，先添加进类型表
        isEx = models.FriendsType.objects.filter(name=data['typeName']).count()
        id = ''
        if isEx != 0:
            #如果已经存在这个类型名，就直接返回id
            typedata = models.FriendsType.objects.get(name=data['typeName'])
            id = typedata.id
        else:
            typeinfo = {
                'name': data['typeName'],
                'count': 1,
            }
            models.FriendsType.objects.create(typeinfo)
            typedata = models.FriendsType.objects.get(name=data['typeName'])
            id = typedata.id
        data['typeId'] = id

    friend = {
        'name': data['name'],
        'url': data['url'],
        'type_id': data['typeId'],
        'update_time': int(time.time()),
    }
    cursor = connection.cursor()
    sql = "select friends_type.count as count,friends_type.id as id from friends,friends_type where friends.friend_id = '%s' and friends.type_id = friends_type.id" % (data['friendId'])
    cursor.execute(sql)
    oldType = dictfetchall(cursor)
    oldCount = oldType[0]['count'] - 1

    newType = models.FriendsType.objects.get(id=data['typeId'])
    newCount = newType['count'] + 1

    models.FriendsType.objects.filter(id=oldType[0]['id']).update(count=oldCount)
    models.FriendsType.objects.filter(id=data['typeId']).update(count=newCount)
    models.Friends.objects.filter(friend_id=data['friendId']).update(friend)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '更新成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def del_friend(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    friendId = get_param(parm, 'friendId')
    if friendId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Friends.filter(friend_id=friendId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    cursor = connection.cursor()
    sql = "select friends_type.count as count,friends_type.id as id from friends,friends_type where friends.friend_id = '%s' and friends.type_id = friends_type.id" % (friendId)
    cursor.execute(sql)
    oldType = dictfetchall(cursor)
    oldCount = oldType[0]['count'] - 1

    models.FriendsType.objects.filter(id=oldType[0]['id']).update(count=oldCount)
    models.Friends.objects.filter(friend_id=friendId).delete()

    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '删除成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def add_category(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    categoryName = get_param(parm, 'categoryName')

    if categoryName == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '分类名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    isEx = models.Category.objects.filter(name=categoryName).count()

    if isEx != 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该分类已经存在，请勿重复添加'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    canDel = get_param(parm, 'canDel')

    canDel = 1 if canDel == '' else 0

    id = str(uuid.uuid1())
    category = {
        'id': id,
        'name': categoryName,
        'create_time': int(time.time()),
        'can_del': canDel,
    }
    models.Category.objects.create(**category)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '更新成功'
    ret['data'] = id
    return HttpResponse(json.dumps(ret))

def modify_category(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    categoryId = get_param(parm, 'categoryId')
    categoryName = get_param(parm, 'categoryName')
    
    if categoryId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '分类id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if categoryName == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '分类名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    isEx = models.Category.objects.filter(id=categoryId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该分类不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    category = models.Category.objects.get(id=categoryId)
    if category.can_del == '0':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '默认分类不可修改'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    category = {
        'name' : categoryName,
        'update_time' : int(time.time()),
    }

    models.Category.objects.filter(id=categoryId).update(**category)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '更新成功'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def del_category(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    categoryId = get_param(parm, 'categoryId')
    if categoryId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    isEx = models.Category.objects.filter(id=categoryId)
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该分类不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    category = models.Category.objects.get(id=categoryId)
    if category.can_del == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '默认分类不可删除'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    models.Category.objects.filter(id=categoryId).delete()

    # 将该分类下的文章移到默认分类中

    defaultCategory = models.Category.objects.filter(can_del=0)
    updatetime = int(time.time())
    if len(defaultCategory) != 0:
        # 获取原分类的文章数量
        count = models.Article.objects.filter(category_id=categoryId).count();

        update = {
            'article_count' : int(defaultCategory.article_count) + int(count),
            'update_time' : updatetime,
        }
        models.Category.objects.filter(id=defaultCategory.id).update(**update)

        models.Article.objects.filter(category_id=categoryId).update(TABLE_ARTICLE, **{'category_id' : defaultCategory.id,'update_time' : updatetime})
        ret["status"] = True
        ret["code"] = 200
        ret["msg"] = '删除成功'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    else:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '无默认分类'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    
def get_category_list(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    pageOpt = get_page(parm)
    all = get_param(parm, 'all')

    count_all = models.Category.objects.filter().count()
    if all == 'true':
        pageOpt['pageSize'] = count_all

    cursor = connection.cursor()
    cursor.execute("select id as categoryId, name as categoryName, create_time as createTime, update_time as updateTime, status, article_count as articleCount, can_del as canDel from category limit %d,%d order by aid desc") % (int(pageOpt['pageSize']), int(pageOpt['page']) * int(pageOpt['pageSize']))
    categoryList = dictfetchall(cursor)    
    result = { 
        'page' : pageOpt['page'],
        'pageSize' : pageOpt['pageSize'],
        'count' : count_all,
        'list' : categoryList,
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))

def get_category(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    categoryId = get_param(parm, 'categoryId')
    if categoryId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    isEx = models.Category.objects.filter(id=categoryId)
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该分类不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    cursor = connection.cursor()
    cursor.execute("select id, name, article_count as articleCount from category where id = '%s'") % (categoryId)
    categoryList = dictfetchall(cursor)    
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = categoryList
    return HttpResponse(json.dumps(ret))

def add_tag(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    tagName = get_param(parm, 'tagName')
    if tagName == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '标签名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    isEx = models.Tag.objects.filter(name=tagName).count()
    if isEx != 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该标签已经存在，请勿重复添加'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    tagId = str(uuid.uuid1())
    tag = {
        'id' : tagId,
        'name' : tagName,
        'create_time' : int(time.time()),
    }
    models.Tag.objects.create(**tag)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = tagId
    return HttpResponse(json.dumps(ret))

def modify_tag(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    tagName = get_param(parm, 'tagName')
    tagId = get_param(parm, 'tagId')
    if tagName == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '标签名称不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if tagId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '标签id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Tag.objects.filter(id=tagId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该标签不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    tag={
        'name' : tagName,
        'update_time' : int(time.time()),
    }
    models.Tag.objects.filter(id=tagId).update(**tag)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def del_tag(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    tagId = get_param(parm, 'tagId')
    if tagId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Tag.objects.filter(id=tagId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该标签不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    # 同时删除所有该 标签-文章 的映射
    models.ArticleTagMapper.objects.filter(tag_id=tagId).delete()
    # 删除标签
    models.Tag.objects.filter(id=tagId).delete()
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = []
    return HttpResponse(json.dumps(ret))

def get_tag_list(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    pageOpt = get_page(parm)
    all = get_param(parm, 'all')
    count_all = models.Tag.objects.filter().count()
    if all == 'true':
        pageOpt['pageSize'] = count_all
    cursor = connection.cursor()
    cursor.execute("select id as tagId, name as tagName, create_time as createTime, update_time as updateTime, status, article_count as articleCount from tag limit %d,%d order by aid desc") % (int(pageOpt['pageSize']), int(pageOpt['page']) * int(pageOpt['pageSize']))
    tagList = dictfetchall(cursor)    
    result = { 
        'page' : pageOpt['page'],
        'pageSize' : pageOpt['pageSize'],
        'count' : count_all,
        'list' : tagList,
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))
    
def get_tag(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    tagId = get_param(parm, 'tagId')
    if tagId == '':
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Tag.objects.filter(id=tagId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -4002
        ret["msg"] = '该标签不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    cursor = connection.cursor()
    cursor.execute("select id, name, article_count as articleCount from tag where id = '%s'") % (tagId)
    tagList = dictfetchall(cursor)    
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = tagList
    return HttpResponse(json.dumps(ret))

def save(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    article = {
        'id' : '',
        'content' : '',
        'htmlContent' : '',
        'title' : '',
        'cover' : '',
        'subMessage' : '',
        'isEncrypt' : '',
    }
    for item in article:
        article[item] = get_param(parm, item)
    number = is_p_number(article['isEncrypt'])
    if number == False:
        article['isEncrypt'] = 0
    else:
        article['isEncrypt'] = int(article['isEncrypt'])
        if article['isEncrypt'] != 0 and article['isEncrypt'] != 1:
            article['isEncrypt'] = 0 
    if article['id'] == '':
        article['id'] = str(uuid.uuid1())
        article['create_time'] = int(time.time())
        article['update_time'] = int(time.time())
        article['status'] = 2
        models.Article.objects.create(**article)
    else:
        isEx = models.Article.objects.filter(id=article['id']).count()
        if isEx == 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '文章不存在'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        article['update_time'] = int(time.time())
        cur = models.Article.objects.get(id=article['id'])
        if cur.status == 1:
            article['status'] = 2
        models.Article.objects.filter(id=article['id']).update(**article)
    userInfo = models.Admin.objects.get(access_token=request.META.get('accessToken', ''))
    save_sys_log('管理员' + userInfo.username + '保存了文章(' + article['id'] + ')')
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = article['id']
    return HttpResponse(json.dumps(ret))
    
def publish(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    article = {
        'id' : '',
        'content' : '',
        'htmlContent' : '',
        'title' : '',
        'cover' : '',
        'subMessage' : '',
        'isEncrypt' : '',
        'category' : '',
        'tags' : '',
    }
    for item in article:
        article[item] = get_param(parm, item)
    if article['title'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '标题不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if article['content'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章内容不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if article['subMessage'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章简介不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    number = is_p_number(article['isEncrypt'])
    if number == False:
        article['isEncrypt'] = 0
    else:
        article['isEncrypt'] = int(article['isEncrypt'])
        if article['isEncrypt'] != 0 and article['isEncrypt'] != 1:
            article['isEncrypt'] = 0 

    # 保存文章基本信息并获取id
    if article['id'] == '':
        article['id'] = str(uuid.uuid1())
        article['create_time'] = int(time.time())
        article['update_time'] = int(time.time())
        article['status'] = 2
        models.Article.objects.create(**article)
    else:
        isEx = models.Article.objects.filter(id=article['id']).count()
        if isEx == 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '文章不存在'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        article['update_time'] = int(time.time())
        cur = models.Article.objects.get(id=article['id'])
        if cur.status == 1:
            article['status'] = 2
        models.Article.objects.filter(id=article['id']).update(**article)
    articleId = article['id'] 

    # 保存分类
    finalcid = ''
    cid = get_param(article['category'], 'id')
    cname = get_param(article['category'], 'name')
    if cid != '':
        isEx = models.Category.objects.filter(id=cid).count()
        if isEx != 0:
            finalcid = cid
    elif cname != '':
        isEx = models.Category.objects.filter(name=cname).count()
        if isEx != 0:
            finalcid = models.Category.objects.filter(name=cname)[0].id
        else:
            category = {
                'id' : str(uuid.uuid1()),
                'name' : cname,
                'create_time' : int(time.time()),
                'can_del' : 1,
            }
            models.Category.objects.create(**category)
            finalcid = category['id']
    else:
        finalcid = models.Category.objects.filter(can_del=0)[0].id

    carticle = {
        'category_id' : cid,
        'update_time' : int(time.time()),
    }

    a = models.Article.objects.filter(id=articleId)


    # 如果文章分类改变，则要将原分类的文章数量-1
    if (a[0].category_id != cid):
        c = models.Category.objects.filter(id=a[0].category_id)

        update = {
            'article_count' : int(c[0].article_count) - 1,
            'update_time' : int(time.time()),
        }
        models.Category.objects.filter(id=a[0].category_id).update(**update)

        category = models.Category.objects.filter(id=finalcid)
    
        update = { 
            'article_count' : int(category[0].article_count) + 1,
            'update_time' : int(time.time()),
        }

        models.Category.objects.filter(id=finalcid).update(**update)

    models.Article.objects.filter(id=articleId).update(**carticle)
    tags = list()
    if article['tags'] != '':
        tmp = json.loads(article['tags'])
        for item in tmp:
            tid = item['id']
            tname = item['name']
            if tid != '':
                isEx = models.Category.objects.filter(id=tid).count()
                if isEx != 0:
                    if tid not in tags:
                        tags.append(tid)
                    continue
            if tname != '':
                isEx = models.Category.objects.filter(name=tname).count()
                tid = ''
                if isEx == 0:
                    tid = str(uuid.uuid1())
                    tagtmp = {
                        'id' : tid,
                        'name' : tname,
                        'create_time' : int(time.time()),
                    }
                    models.Category.objects.create(**tagtmp)
                else:
                    tid = models.Category.objects.filter(name=tname)[0].id
                if tid not in tags:
                    tags.append(tid)
    for item in tags:
        isEx = models.Article.objects.filter(id=articleId).count()
        if isEx == 0:
            continue
        isEx = models.Tag.objects.filter(id=item).count()
        if isEx == 0:
            continue
        conditions = {
            'article_id' : articleId,
            'tag_id' : item,
        }
        isEx = models.ArticleTagMapper.filter(**conditions).count()
        if isEx != 0:
            continue
        mapper = {
            'article_id' : articleId,
            'tag_id' : item,
            'create_time' : int(time.time()),
        } 
        tagupdate = {
            'article_count' : int(models.Tag.objects.filter(id=item)[0].article_count) + 1,
            'update_time' : int(time.time()),
        }
        models.Tag.objects.filter(id=item).update(**tagupdate)
        models.ArticleTagMapper.objects.create(**mapper)
    articletmp = {
        'publish_time' : int(time.time()),
        'status' : 0,
    }
    models.Article.objects.filter(id=articleId).update(articletmp)
    save_sys_log('管理员' + userInfo.username + '发布了文章(' + article['id'] + ')')
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = articleId
    return HttpResponse(json.dumps(ret))
    
def modify(request):        
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    article = {
        'id' : '',
        'content' : '',
        'htmlContent' : '',
        'title' : '',
        'cover' : '',
        'subMessage' : '',
        'isEncrypt' : '',
        'category' : '',
        'tags' : '',
    }
    for item in article:
        article[item] = get_param(parm, item)
    if article['id'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if article['title'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '标题不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if article['content'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章内容不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if article['subMessage'] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章简介不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    number = is_p_number(article['isEncrypt'])
    if number == False:
        article['isEncrypt'] = 0
    else:
        article['isEncrypt'] = int(article['isEncrypt'])
        if article['isEncrypt'] != 0 and article['isEncrypt'] != 1:
            article['isEncrypt'] = 0 
    isEx = models.Article.objects.filter(id=article['id']).count() 
    if isEx != 0:
        tmp = models.Article.objects.filter(id=article['id'])
        if tmp[0].status != 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '文章不可调用该编辑借口'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
    else:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    # 保存分类
    finalcid = ''
    cid = get_param(article['category'], 'id')
    cname = get_param(article['category'], 'name')
    if cid != '':
        isEx = models.Category.objects.filter(id=cid).count()
        if isEx != 0:
            finalcid = cid
    elif cname != '':
        isEx = models.Category.objects.filter(name=cname).count()
        if isEx != 0:
            finalcid = models.Category.objects.filter(name=cname)[0].id
        else:
            category = {
                'id' : str(uuid.uuid1()),
                'name' : cname,
                'create_time' : int(time.time()),
                'can_del' : 1,
            }
            models.Category.objects.create(**category)
            finalcid = category['id']
    else:
        finalcid = models.Category.objects.filter(can_del=0)[0].id
    carticle = {
        'category_id' : cid,
        'update_time' : int(time.time()),
    }

    a = models.Article.objects.filter(id=articleId)


    # 如果文章分类改变，则要将原分类的文章数量-1
    if (a[0].category_id != cid):
        c = models.Category.objects.filter(id=a[0].category_id)

        update = {
            'article_count' : int(c[0].article_count) - 1,
            'update_time' : int(time.time()),
        }
        models.Category.objects.filter(id=a[0].category_id).update(**update)

        category = models.Category.objects.filter(id=finalcid)
    
        update = { 
            'article_count' : int(category[0].article_count) + 1,
            'update_time' : int(time.time()),
        }

        models.Category.objects.filter(id=finalcid).update(**update)

    # 保存标签（添加新的，并删除旧的） 
    tagList = models.ArticleTagMapper.objects.filter(article_id=article['id']) 
    oldTags = list()
    for item in tagList:
        oldTags.append(item) 
    tags = list()
    if article['tags'] != '':
        tmp = json.loads(article['tags'])
        for item in tmp:
            tid = item['id']
            tname = item['name']
            if tid != '':
                isEx = models.Category.objects.filter(id=tid).count()
                if isEx != 0:
                    if tid not in tags:
                        tags.append(tid)
                    continue
            if tname != '':
                isEx = models.Category.objects.filter(name=tname).count()
                tid = ''
                if isEx == 0:
                    tid = str(uuid.uuid1())
                    tagtmp = {
                        'id' : tid,
                        'name' : tname,
                        'create_time' : int(time.time()),
                    }
                    models.Category.objects.create(**tagtmp)
                else:
                    tid = models.Category.objects.filter(name=tname)[0].id
                if tid not in tags:
                    tags.append(tid)

    for item in tags:
        if item in oldTags:
            oldTags.remove(item)
        else:
            isEx = models.Article.objects.filter(id=article['id']).count()
            if isEx == 0:
                continue
            isEx = models.Tag.objects.filter(id=item).count()
            if isEx == 0:
                continue
            conditions = {
                'article_id' : article['id'],
                'tag_id' : item,
            }
            isEx = models.ArticleTagMapper.filter(**conditions).count()
            if isEx != 0:
                continue
            mapper = {
                'article_id' : article['id'],
                'tag_id' : item,
                'create_time' : int(time.time()),
            } 
            tagupdate = {
                'article_count' : int(models.Tag.objects.filter(id=item)[0].article_count) + 1,
                'update_time' : int(time.time()),
            }
            models.Tag.objects.filter(id=item).update(**tagupdate)
            models.ArticleTagMapper.objects.create(**mapper)
    for item in oldTags:
        tag = models.Tag.objects.filter(id=item)
        update = {
            'article_count' : int(tag[0].article_count) - 1,
            'update_time' : int(time.time()),
        }
        models.Tag.objects.filter(id=item).update(**update)
        conditions = {
            'tag_id' : item,
            'article_id' : article['id'],
        }
        models.ArticleTagMapper.filter(**conditions).delete()
    article['update_time'] = int(time.time()) 
    a = models.Article.objects.filter(id=article['id'])
    if a[0].status == '1':
        article['status'] = 2
    models.Article.objects.filter(id=article['id']).update(**article)
    save_sys_log('管理员' + userInfo.username + '编辑了文章(' + article['id'] + ')')
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = article['id']
    return HttpResponse(json.dumps(ret))

def delete(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    articleId = get_param(parm, 'id')
    if articleId == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Article.objects.filter(id=articleId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    tagList = models.ArticleTagMapper.objects.filter(article_id=articleId).count()
    if len(tagList) > 0:
        t = int(time.time())
        for item in tagList:
            tag = models.Tag.objects.filter(id=item.tag_id)
            update = {
                'article_count' : int(tag[0].article_count) - 1,
                'update_time' : t,
            }
            models.Tag.objects.filter(id=tag[0].id).update(**update)
        models.ArticleTagMapper.objects.filter(article_id=articleId).delete()
    articletmp = models.Article.objects.filter(id=articleId)
    t = int(time.time())
    if articletmp[0].status == '1':
        models.Article.objects.filter(id=articleId).delete()
    else:
        data = {
            'category_id' : '',
            'status' : '2',
            'delete_time' : t,
            'update_time' : t,
        }
        if articletmp[0].status == '2':
            data['status'] = '1'
        models.Article.objects.filter(id=articleId).update(**data)
    if articletmp[0].status == '0':
        c = models.Category.objects.filter(id=articletmp[0].category_id)
        update = {
            'article_count' : int(c[0].article_count) - 1,
            'update_time' : t,
        }
        models.Category.objects.filter(id=articletmp[0].category_id).update(**update)
    models.Comments.objects.filter(article_id=articleId).delete()
    save_sys_log('管理员' + userInfo.username + '删除了文章(' + article['id'] + ')')
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = '已删除'
    ret['data'] = [] 
    return HttpResponse(json.dumps(ret))

def get_article(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    articleId = get_param(parm, 'id')
    if articleId == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Article.objects.filter(id=articleId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章不存在'
        ret['data'] = []
    cursor = connection.cursor()
    cursor.execute("select id, title, cover, sub_message as subMessage, content, html_content as htmlContent, pageview, status, category_id as categoryId, is_encrypt as isEncrypt, publish_time as publishTime, create_time as createTime, update_time as updateTime, delete_time as deleteTime from article where id = '%s'" % articleId)
    article = dictfetchall(cursor)
    cursor.execute("select id, name from category where id = '%s'" % article[0]["categoryId"])
    category = dictfetchall(cursor)
    cursor.execute("select tag.id, tag.name from article_tag_mapper,tag where article_tag_mapper.article_id = '%s' and tag.id = article_tag_mapper.tag_id" % articleId)
    tags = dictfetchall(cursor)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = {
        "article" : article,
        "category" : category,
        "tags" : tags,
    }
    return HttpResponse(json.dumps(ret))
    
def get_article_list(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    by = get_param(parm, 'by')
    status = get_param(parm, 'status')
    categoryId = get_param(parm, 'categoryId')
    tagId = get_param(parm, 'tagId')
    pageOpt = get_page(parm)
    result = dict()
    if by == 'category':
        if categoryId == '':
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '分类id不能为空'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        isEx = models.Category.objects.filter(id=categoryId).count()
        if isEx == 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '不存在该分类'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        cursor = connection.cursor()
        cursor.execute("select article.id as id, title, cover, pageview, article.status as status, is_encrypt as isEncrypt, category.name as categoryName,article.create_time as createTime, article.update_time as updateTime, article.publish_time as publishTime, article.delete_time as deleteTime from article,category where article.category_id = '%s' and article.id != '-1' and category.id = article.category_id order by article.update_time desc" % categoryId)
        articleDB = dictfetchall(cursor)
        result = {
            "page" : pageOpt['page'],
            "pageSize" : pageOpt['pageSize'],
            "count" : len(articleDB),
            "list" : articleDB[pageOpt['pageSize']:pageOpt['page']*pageOpt['pageSize']], 
        }
    elif by == 'tag':
        if tagId == '':
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '标签id不能为空'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        isEx = models.Tag.objects.filter(id=tagId).count()
        if isEx == 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '不存在该标签'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        cursor = connection.cursor()
        cursor.execute("select article.id as id, title, cover, pageview, article.status as status, is_encrypt as isEncrypt, category.name as categoryName,article.create_time as createTime, article.update_time as updateTime, article.publish_time as publishTime, article.delete_time as deleteTime from article,category,article_tag_mapper where article.category_id = category.id and article_tag_mapper.article_id = article.id and article.id != '-1' and article_tag_mapper.tag_id = '%s' order by article.update_time desc" % tagId)
        articleDB = dictfetchall(cursor)
        result = {
            "page" : pageOpt['page'],
            "pageSize" : pageOpt['pageSize'],
            "count" : len(articleDB),
            "list" : articleDB[pageOpt['pageSize']:pageOpt['page']*pageOpt['pageSize']], 
        }
    else:
        if status != '0' and status != '-1' and status != '-2':
            status = False
        cursor = connection.cursor()
        if status == False:
            cursor.execute("select article.id as id, title, cover, pageview, article.status as status, is_encrypt as isEncrypt, category.name as categoryName,article.create_time as createTime, article.update_time as updateTime, article.publish_time as publishTime, article.delete_time as deleteTime from article,category,article_tag_mapper where article.id != '-1' and category.id = article.category_id order by article.update_time desc")
        else:
            cursor.execute("select article.id as id, title, cover, pageview, article.status as status, is_encrypt as isEncrypt, category.name as categoryName,article.create_time as createTime, article.update_time as updateTime, article.publish_time as publishTime, article.delete_time as deleteTime from article,category,article_tag_mapper where article.id != '-1' and category.id = article.category_id and article.status = '%s' order by article.update_time desc" % status)
        articleDB = dictfetchall(cursor)
        result = {
            "page" : pageOpt['page'],
            "pageSize" : pageOpt['pageSize'],
            "count" : len(articleDB),
            "list" : articleDB[pageOpt['pageSize']:pageOpt['page']*pageOpt['pageSize']], 
        }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))

def get_sys_log(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    pageOpt = get_page(parm)
    logDB = models.SysLog.objects.filter().order_by('-time') 
    
    data = {
        "page" : pageOpt['page'],
        "pageSize" : pageOpt['pageSize'] * pageOpt['page'],
        "count" : len(logDB),
        "list" : logDB[pageOpt['pageSize']:(pageOpt['pageSize'] + pageOpt['pageSize'] * pageOpt['page'])],
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = data
    return HttpResponse(json.dumps(ret))

def get_home_statistics(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    publishCount = models.Article.objects.filter(status=0).exclude(id="-1").count()
    draftsCount = models.Article.objects.filter(status=2).exclude(id="-1").count()
    deletedCount = models.Article.objects.filter(status=1).exclude(id="-1").count()
    categoryCount = models.Category.objects.filter().count()
    tagCount = models.Tag.objects.filter().count()
    commentsCount = models.Comments.objects.filter().count()
    result = {
        "publishCount" : publishCount,
        "draftsCount" : draftsCount,
        "deletedCount" : deletedCount,
        "categoryCount" : categoryCount,
        "tagCount" : tagCount,
        "commentsCount" : commentsCount,
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))

def get_comments(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    articleId = get_param(parm, 'articleId')
    isEx = models.Article.objects.filter(id=articleId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '不存在该文章'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    cursor = connection.cursor()
    cursor.execute("select id, parent_id as parentId, article_id as articleId, reply_id as replyId, name, content, create_time as createTime, is_author as isAuthor from comments where status = '0' and article_id = %s and parent_id = '0' order by create_time desc" % articleId)
    list = dictfetchall(cursor)
    lists = list()
    for item in list:
        children = cursor.execute("select id, parent_id as parentId, article_id as articleId, reply_id as replyId, name, content, create_time as createTime, is_author as isAuthor from comments where status = '0' and article_id = %s and parent_id = %s order by create_time desc" % (articleId, item["id"]))
        item['children'] = children
        lists.append(item)
    count = models.Comments.objects.filter().count()
    result = {
        "count" : count,
        "list" : lists,
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))

def comments_add(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    data = {
        "content" : '',
        "articleId" : '',
        "replyId" : '',
        "sourceContent" : '',
    }
    for key in data:
        data[key] = get_param(parm, key)
    if data["content"] == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '评论内容不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    isEx = models.Article.objects.filter(id=data["articleId"]).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = 'false'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    if data['replyId'] == 0:
        data['parentId'] = 0
    else:
        isex = models.Comments.objects.filter(id=data['replyId']).count()
        if isex == 0:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '评论不存在'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        comments = models.Comments.objects.filter(id=data['replyId'])
        if comments[0].article_id != data['articleId']:
            ret["status"] = False
            ret["code"] = -1
            ret["msg"] = '文章与评论不匹配'
            ret['data'] = []
            return HttpResponse(json.dumps(ret))
        if commemts[0].parent_id == '0':
            data['parentId'] = comments[0].id
        else:
            data['parentId'] = comments[0].parent_id
    
    userInfo = models.Admin.objects.get(access_token=request.META.get('accessToken', ''))
    comment = {
        "name" : userInfo.username, 
        "content" : data["content"],
        "source_content" : data["sourceContent"],
        "create_time" : int(time.time()),
        "article_id" : data["articleId"],
        "reply_id" : data["replyId"],
        "parent_id" : data["parentId"],
        "is_author" : 1,
    }
    models.Comments.objects.create(**comment)
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = "留言成功" if data[articleId] == '-1' else "评论成功"
    return HttpResponse(json.dumps(ret))
    
def comments_delete(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.POST
    commentsId = get_param(parm, 'commentsId')
    isEx = models.Comments.objects.filter(id=commentsId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '评论不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    models.Comments.objects.filter(Q(id=commentsId)|Q(parent_id=commentsId)|Q(reply_id=commentsId)).delete() 
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = "已删除"
    return HttpResponse(json.dumps(ret))

def get_all_comments(request):
    ret = dict()
    if check_token(request) == False:
        ret["status"] = False
        ret["code"] = -4001
        ret["msg"] = '无效的token'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    parm = request.GET
    pageOpt = get_page(parm)
    cursor = connection.cursor()
    cursor.execute("select comments.id as id, parent_id as parentId, article_id as articleId, reply_id as replyId, name, comments.content as content, comments.create_time as createTime, is_author as isAuthor, article.title as articleTitle, comments.status as status from comments,article where article.id = comments.article_id order by comments.create_time desc")
    result = dictfetchall(cursor)
    data = {
        "page" : pageOpt['page'],
        "pageSize" : pageOpt['pageSize'],
        "count" : len(result),
        "list" : result[pageOpt['pageSize'] : (pageOpt['page'] * pageOpt['pageSize'])],
    }
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = data
    return HttpResponse(json.dumps(ret))

