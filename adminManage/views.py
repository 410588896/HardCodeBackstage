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

def get_web_config(request):
	config = models.BlogConfig.objects.values_list('blog_name', 'avatar', 'sign', 'wxpay_qrcode', 'alipay_qrcode', 'github', 'salt')
	
    $config = $this->db->from(TABLE_BLOG_CONFIG)
                            ->select('blog_name as blogName, avatar, sign, wxpay_qrcode as wxpayQrcode,
                                    alipay_qrcode as alipayQrcode, github, salt')
                            ->get()
                            ->row_array();
        
        if ($config && $config['salt']) {
            $config['hadOldPassword'] = true;
        } else {
            $config['hadOldPassword'] = false;
        }
        if (!$config) {
            $config = false;
        }
        unset($config['salt']);
        
       return success($config);
    }

    public function modify($params)
    {
        $config = $this->db->from(TABLE_BLOG_CONFIG)
                            ->get()
                            ->row_array();

        if ($config) {
            if ($params['settingPassword'] == 'true') {
                // 如果有秘钥存在，说明已经有设置过密码了，要对密码进行比较
                if ($config['salt']) {
                    if (!cb_passwordEqual($config['view_password'], $config['salt'], $params['oldPassword'])) {
                        return fail('原密码错误');
                    }
                }
                // 加密新密码
                $encrypt = cb_encrypt($params['viewPassword']);
                $config['view_password'] = $encrypt['password'];
                $config['salt'] = $encrypt['salt'];
            }
            $config['blog_name'] = $params['blogName'];
            $config['avatar'] = $params['avatar'];
            $config['sign'] = $params['sign'];
            $config['wxpay_qrcode'] = $params['wxpayQrcode'];
            $config['alipay_qrcode'] = $params['alipayQrcode'];
            $config['github'] = $params['github'];

            $this->db->where('id', $config['id'])->update(TABLE_BLOG_CONFIG, $config);
        } else {
            $config = array();
            if ($params['settingPassword'] == 'true') {
                // 加密新密码
                $encrypt = cb_encrypt($params['viewPassword']);
                $config['view_password'] = $encrypt['password'];
                $config['salt'] = $encrypt['salt'];
            }
            $config['blog_name'] = $params['blogName'];
            $config['avatar'] = $params['avatar'];
            $config['sign'] = $params['sign'];
            $config['wxpay_qrcode'] = $params['wxpayQrcode'];
            $config['alipay_qrcode'] = $params['alipayQrcode'];
            $config['github'] = $params['github'];

            $this->db->insert(TABLE_BLOG_CONFIG, $config);
        }
        
        return success('更新成功');
    }

    public function get_about_me()
    {
        $config = $this->db->from(TABLE_PAGES)
                            ->select('type, md, html')
                            ->where('type', 'about')
                            ->get()
                            ->row_array();
        if (!$config) {
            $config = array();
        }
        if (!isset($config['md'])) {
            $config['md'] = '';
        }
        if (!isset($config['html'])) {
            $config['html'] = '';
        }

        return success($config);
    }

    public function modify_about($content, $htmlContent)
    {
        $config = $this->db->from(TABLE_PAGES)
                            ->where('type', 'about')
                            ->get()
                            ->row_array();
        if ($config) {
            $this->db->where('id', $config['id'])->update(TABLE_PAGES, array('md'=> $content, 'html'=> $htmlContent));
        } else {
            $this->db->insert(TABLE_PAGES, array('md'=> $content, 'html'=> $htmlContent, 'type'=> 'about'));
        }
        
        return success('更新成功');
    }

    public function get_resume()
    {
        $config = $this->db->from(TABLE_PAGES)
                            ->select('type, md, html')
                            ->where('type', 'resume')
                            ->get()
                            ->row_array();
        if (!$config) {
            $config = array();
        }
        if (!isset($config['md'])) {
            $config['md'] = '';
        }
        if (!isset($config['html'])) {
            $config['html'] = '';
        }

        return success($config);
    }

    public function modify_resume($content, $htmlContent)
    {
        $config = $this->db->from(TABLE_PAGES)
                            ->where('type', 'resume')
                            ->get()
                            ->row_array();
        if ($config) {
            $this->db->where('id', $config['id'])->update(TABLE_PAGES, array('md'=> $content, 'html'=> $htmlContent));
        } else {
            $this->db->insert(TABLE_PAGES, array('md'=> $content, 'html'=> $htmlContent, 'type'=> 'resume'));
        }
        
        return success('更新成功');
    }
