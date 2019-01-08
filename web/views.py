# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

from adminManage import models

from django.db import connection

import time

from utils import *

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

def get_article_archives(request):
    parm = request.GET
    pageOpt = get_page(parm)
    count = models.Article.objects.filter(status='0').exclude(id='-1').count()
    cursor = connection.cursor()
    cursor.execute("select id,title,cover,sub_message as subMessage,pageview,status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article where status='0' and id!='-1' order by publish_time desc limit %s, %s", (int(pageOpt['page']), int(pageOpt['page'])*pageOpt['pageSize']))
    articleDB = dictfetchall(cursor)
    result = list()
    for item in articleDB:
        category = models.Category.filter(id=item['categoryId']).get('id', 'name')
        cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id")
        tagret = cursor.fetchall()
        tags_list = list()
        for subitem in tagret:
            tags_list.append({'id':subitem[0], 'name':subitem[1]})

        result.append({'article':item, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list})

    #将文章按年月归类
    year = dict()
    for item in result:
        timeStamp = item['article']['publishTime']
        timeArray = time.localtime(timeStamp)
        year_tmp  = time.strftime("%Y", timeArray)
        month_tmp  = time.strftime("%m", timeArray)
        if year.has_key(year_tmp+'年'):
            if year[year_tmp+'年'].has_key(month_tmp+'月'):
                year[year_tmp+'年'][month_tmp+'月'].append(item)
            else:
                year[year_tmp+'年'][month_tmp+'月'] = [item]
        else:
            year[year_tmp+'年'] = {month_tmp+'月': [item]}

    retdata = dict()
    retdata['page'] = pageOpt['page']
    retdata['pageSize'] = pageOpt['pageSize'] 
    retdata['count'] = count
    retdata['list'] = year
    ret = dict()
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))
    
def get_article(request):
    pass
