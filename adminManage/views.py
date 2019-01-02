# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

def login(request):
    #检查用户名是否存在
    ret = dict()
    $isEx = $this->db->where('username', $username)->count_all_results(TABLE_ADMIN);
    if $isEx == 0 :
    	ret["status"] = False
    	ret["code"] = -1
    	ret["msg"] = '该账号不存在'
    	ret['data'] = []
        return ret

        $adminInfo = $this->db->where('username', $username)
                            ->from(TABLE_ADMIN)
                            ->get()
                            ->row_array();

        switch($adminInfo['status']) {
            case '0':
                break;
            default:
                return fail('账号异常');
        }

        if (!cb_passwordEqual($adminInfo['password'], $adminInfo['salt'], $password)) {
            return fail('密码错误');
        }

        $time = time();

        $data = array(
            'last_login_time' => $time,
            'access_token' => create_id(),
            'token_expires_in' => $time + WEEK
        );

        // 更新数据
        $this->db->where('username', $username)->update(TABLE_ADMIN, $data);

        $adminInfo = $this->db->where('username', $username)
                            ->from(TABLE_ADMIN)
                            ->get()
                            ->row_array();

        $userResult = array(
            'userId' => $adminInfo['user_id'],
            'userName' => $adminInfo['username'],
            'lastLoginTime' => $adminInfo['last_login_time'],
            'token' => array(
                'accessToken' => $adminInfo['access_token'],
                'tokenExpiresIn' => $adminInfo['token_expires_in'],
                'exp' => WEEK
            )
        );
        
        return success($userResult);
    return HttpResponse("Hello, world. You're at the polls index.")

def get_qiniu_token(request):
    return HttpResponse("Hello, world. You're at the polls index.")
