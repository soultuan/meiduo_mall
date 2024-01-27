import re

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from apps.users.models import User


# Create your views here.
class UsernameCountView(View):

    def get(self,request,username):
        # 1.接收用户名，对这个用户名进行判断
        # if not re.match('[a-zA-Z0-9_-]{5,20}',username):
        #     return JsonResponse({'code':200,'errmsg':'用户名不满足规范'})
        # 2.根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        # 3.返回响应
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})