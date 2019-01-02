# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

def login(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def get_qiniu_token(request):
    return HttpResponse("Hello, world. You're at the polls index.")
