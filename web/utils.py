# -*- coding: utf-8 -*-
from __future__ import unicode_literals

def is_p_number(num):
    try:
        z=int(num)
        return isinstance(z,int)
    except ValueError:
        return False

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

def dictfetchall(cursor): 
    '''Returns all rows from a cursor as a dict'''
    desc = cursor.description 
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] 
