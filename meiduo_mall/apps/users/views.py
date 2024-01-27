from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from apps.users.models import User


# Create your views here.
class UsernameCountView(View):

    def get(self,request,username):
        # 1.接收用户名
        # 2.根据用户名查询数据库
        count = User.objects.filter(username=username).count()
        # 3.返回响应
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})