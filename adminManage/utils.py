# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
from random import Random

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
