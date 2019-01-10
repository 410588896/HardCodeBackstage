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
    cursor.execute("select id,title,cover,sub_message as subMessage,pageview,status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article where status='0' and id!='-1' order by publish_time desc limit %s, %s", (int(pageOpt['pageSize']), int(pageOpt['page'])*pageOpt['pageSize']))
    articleDB = dictfetchall(cursor)
    result = list()
    for item in articleDB:
        category = models.Category.filter(id=item['categoryId']).get('id', 'name')
        cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [item['id']])
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
    ret = dict()
    parm = request.GET
    articleId = get_param(parm, 'id')
    if articleId == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = 'id不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    #检测文章是否存在
    isEx = models.Article.objects.filter(id=articleId).count()
    if isEx == 0:
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '文章不存在'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))
    
    article = models.Article.objects.get(id=articleId)
    articleinfo = {
            'id':article.id,
            'title':article.title,
            'cover':article.cover,
            'subMessage':article.sub_message,
            'htmlContent':article.html_content,
            'pageview':article.pageview,
            'status':article.status,
            'categoryId':article.category_id,
            'isEncrypt':article.is_encrypt,
            'publishTime':article.publish_time,
            'createTime':article.create_time,
            'updateTime':article.update_time,
            'deleteTime':article.delete_time,
    }
    articleinfo['pageview'] += 1 
    models.Article.objects.filter(id=articleId).update(**{'pageview':articleinfo['pageview']})
    category = models.Category.filter(id=articleinfo['categoryId']).get('id', 'name')
    cursor = connection.cursor()
    cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [articleinfo['id']])
    tagret = cursor.fetchall()
    tags_list = list()
    for item in tagret:
        tags_list.append({'id':item[0], 'name':item[1]})

    result = {'article':articleinfo, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list}

    config_num = models.BlogConfig.objects.all().count()
    qrcode = dict()
    if config_num == 0:
        qrcode['wxpayQrcode'] = ''
        qrcode['alipayQrcode'] = ''
    else:
        config = models.BlogConfig.objects.get('wxpay_qrcode', 'alipay_qrcode')
        qrcode['wxpayQrcode'] = config.wxpay_qrcode
        qrcode['alipayQrcode'] = config.alipay_qrcode

    cursor.execute("select id, title from article where status = '0' and publish_time >= %s and id not in (%s, '-1') order by publish_time asc", [articleinfo[publishTime], articleinfo['id']])
    pre = dictfetchall(cursor)
    if len(pre) == 0:
        pre = None
    else:
        pre = pre[0]

    cursor.execute("select id, title from article where status = '0' and publish_time <= %s and id not in (%s, '-1') order by publish_time desc", [articleinfo[publishTime], articleinfo['id']])
    next = dictfetchall(cursor)
    if len(next) == 0:
        next = None
    else:
        next = next[0]

    result['qrcode'] = qrcode
    result['pn'] = {'pre':pre,'next':next}

    ret = dict()
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = result
    return HttpResponse(json.dumps(ret))

def get_article_list(request):
    ret = dict()
    parm = request.GET
    by = get_param(parm, 'by')
    categoryId = get_param(parm, 'categoryId')
    tagId = get_param(parm, 'tagId')
    pageOpt = get_page(parm)

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

        count = models.Article.objects.filter(status='0',category_id=categoryId).exclude(id='-1').count()
        cursor = connection.cursor()
        cursor.execute("select id,title,cover,sub_message as subMessage,pageview,status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article where status='0' and id!='-1' and category_id = '%s' order by publish_time desc limit %s, %s", (categoryId, int(pageOpt['pageSize']), int(pageOpt['page'])*pageOpt['pageSize']))
        articleDB = dictfetchall(cursor)
        result = list()
        for item in articleDB:
            category = models.Category.filter(id=item['categoryId']).get('id', 'name')
            cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [item['id']])
            tagret = cursor.fetchall()
            tags_list = list()
            for subitem in tagret:
                tags_list.append({'id':subitem[0], 'name':subitem[1]})
            result.append({'article':item, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list})
        retdata = dict()
        retdata['page'] = pageOpt['page']
        retdata['pageSize'] = pageOpt['pageSize'] 
        retdata['count'] = count
        retdata['list'] = result
        ret["status"] = True
        ret["code"] = 200
        ret["msg"] = 'success'
        ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
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
        cursor.execute("select count(*) from article,article_tag_mapper where article.status='0' and article.id!='-1' and article_tag_mapper.tag_id = %s", (tagId))
        count = cursor.fetchone()[0] 
        cursor.execute("select article.id as id,title,cover,sub_message as subMessage,pageview,article.status as status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article,article_tag_mapper where article.status='0' and article.id!='-1' and article_tag_mapper.tag_id = %s order by article.publish_time desc limit %s, %s", (tagId, int(pageOpt['pageSize']), int(pageOpt['page'])*pageOpt['pageSize']))
        articleDB = dictfetchall(cursor)
        result = list()
        for item in articleDB:
            category = models.Category.filter(id=item['categoryId']).get('id', 'name')
            cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [item['id']])
            tagret = cursor.fetchall()
            tags_list = list()
            for subitem in tagret:
                tags_list.append({'id':subitem[0], 'name':subitem[1]})
            result.append({'article':item, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list})
        retdata = dict()
        retdata['page'] = pageOpt['page']
        retdata['pageSize'] = pageOpt['pageSize'] 
        retdata['count'] = count
        retdata['list'] = result
        ret["status"] = True
        ret["code"] = 200
        ret["msg"] = 'success'
        ret['data'] = retdata
        return HttpResponse(json.dumps(ret))
    else:
        count = models.Article.objects.filter(status='0').exclude(id='-1').count()
        cursor = connection.cursor()
        cursor.execute("select id,title,cover,sub_message as subMessage,pageview,status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article where status='0' and id!='-1' order by publish_time desc limit %s, %s", (int(pageOpt['pageSize']), int(pageOpt['page'])*pageOpt['pageSize']))
        articleDB = dictfetchall(cursor)
        result = list()
        for item in articleDB:
            category = models.Category.filter(id=item['categoryId']).get('id', 'name')
            cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [item['id']])
            tagret = cursor.fetchall()
            tags_list = list()
            for subitem in tagret:
                tags_list.append({'id':subitem[0], 'name':subitem[1]})
            result.append({'article':item, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list})
        retdata = dict()
        retdata['page'] = pageOpt['page']
        retdata['pageSize'] = pageOpt['pageSize'] 
        retdata['count'] = count
        retdata['list'] = result
        ret["status"] = True
        ret["code"] = 200
        ret["msg"] = 'success'
        ret['data'] = retdata
        return HttpResponse(json.dumps(ret))

def search(request):
    ret = dict()
    parm = request.GET

    searchValue = get_param(parm, 'searchValue')
    pageOpt = get_page(parm)

    if searchValue == '':
        ret["status"] = False
        ret["code"] = -1
        ret["msg"] = '搜索内容不能为空'
        ret['data'] = []
        return HttpResponse(json.dumps(ret))

    count = models.Article.objects.filter(status='0').exclude(id='-1').count()
    cursor = connection.cursor()
    sql = "select count(*) from article where status='0' and id!='-1' and (title like '%%%s%%' or sub_message like '%%%s%%')" % (searchValue, searchValue)
    cursor.execute(sql)
    count = cursor.fetchone()[0] 
    sql = "select id,title,cover,sub_message as subMessage,pageview,status,category_id as categoryId,is_encrypt as isEncrypt,publish_time as publishTime,create_time as createTime,update_time as updateTime,delete_time as deleteTime from article where status='0' and id!='-1' and (title like '%%%s%%' or sub_message like '%%%s%%') order by publish_time desc limit %s, %s" % (searchValue, searchValue, int(pageOpt['pageSize']), int(pageOpt['page'])*pageOpt['pageSize'])
    cursor.execute(sql)
    articleDB = dictfetchall(cursor)
    result = list()
    for item in articleDB:
        category = models.Category.filter(id=item['categoryId']).get('id', 'name')
        cursor.execute("select tag.id, tag.name from tag, article_tag_mapper where article_tag_mapper.article_id = %s and tag.id = article_tag_mapper.tag_id", [item['id']])
        tagret = cursor.fetchall()
        tags_list = list()
        for subitem in tagret:
            tags_list.append({'id':subitem[0], 'name':subitem[1]})
        result.append({'article':item, 'category':{'id':category.id, 'name':category.name}, 'tags':tags_list})
    retdata = dict()
    retdata['page'] = pageOpt['page']
    retdata['pageSize'] = pageOpt['pageSize'] 
    retdata['count'] = count
    retdata['list'] = result
    ret["status"] = True
    ret["code"] = 200
    ret["msg"] = 'success'
    ret['data'] = retdata
    return HttpResponse(json.dumps(ret))
