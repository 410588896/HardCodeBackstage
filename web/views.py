# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from adminManage import models

import json

def get_about_me(request):
    ret = dict()
    isEx = models.Pages.objects.filter(type='about').count()
    if isEx == 0:
        retdata = dict()
        retdata['html'] = ''
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
       
    if isEx != 0:
        config = models.Pages.objects.get(type='about')
        retdata = dict()
        if config.html == 'null':
            retdata['html'] == ''
        else:
            retdata[html] = config.html
        
        retdata['md'] = config.md
        retdata['type'] = config.type
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
        
def get_resume(request):
    ret = dict()
    isEx = models.Pages.objects.filter(type='resume').count()
    if isEx == 0:
        retdata = dict()
        retdata['html'] = ''
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
       
    if isEx != 0:
        config = models.Pages.objects.get(type='resume')
        retdata = dict()
        if config.html == 'null':
            retdata['html'] == ''
        else:
            retdata[html] = config.html
        
        retdata['md'] = config.md
        retdata['type'] = config.type
    	ret["status"] = True
    	ret["code"] = 0
    	ret["msg"] = '查询成功'
    	ret['data'] = retdata
        return HttpResponse(json.dumps(ret))

def get_blog_info(request):
    retdata = dict()
    ret = dict()
    config = models.BlogConfig.objects.values_list('blog_name', 'avatar', 'sign', 'github')
    if len(config) != 0:
        retdata['blogName'] = config[0][0]
        retdata['avatar'] = config[0][1]
        retdata['sign'] = config[0][2]
        retdata['github'] = config[0][3]
    else:
        retdata['blogName'] = ''
        retdata['avatar'] = ''
        retdata['sign'] = ''
        retdata['github'] = ''
    count_all = models.Article.objects.filter(status='0').exclude(id='-1').count()
    retdata['articleCount'] = count_all
    count_all = models.Category.objects.filter(article_count__gt=0).count()
    retdata['categoryCount'] = count_all
    count_all = models.Tag.objects.filter(article_count__gt=0).count()
    retdata['tagCount']= count_all
    ret["status"] = True
    ret["code"] = 0
    ret["msg"] = '查询成功'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))

