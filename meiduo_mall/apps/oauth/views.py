from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.settings import QQ_CLIENT_ID,QQ_CLIENT_SECRET,QQ_REDIRECT_URI
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
from django_redis import get_redis_connection
from apps.users.models import User
from apps.oauth.utils import generic_openid,check_access_token

import json,re
# Create your views here.
# 1.准备工作
#     QQ登录参数
#     我们申请的客户端id
#     QQ_CLIENT_ID = '101474184'------appid
#     我们申请的客户端密钥
#     QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'-------appkey
#     我们申请时添加的：登陆成功后回调的路径
#     QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
#
# 2.放置QQ登录的图标
#
# 3.根据oauth2.0来获取code和token
#     对于不同应用而言，需要进行两步：
#     1.获取Authorization Code
#     2.通过Authorization Code获得Authorization token
#
# 4.通过token换取openid
#     openid是此网站上唯一对应与用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨别身份，
#     或将其与用户在网站上的原有账户进行绑定

class QQLoginURLView(View):

    def get(self,request):
        # 1.生成QQLoginTool实例
        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI,
                     state='None')
        # 2.调用对象的方法生成跳转链接
        qq_login_url = qq.get_qq_url()
        # 3.返回响应
        return JsonResponse({'code':0,'errmsg':'ok','login_url':qq_login_url})

class OAuthQQView(View):

    def get(self,request):
        # 1.获取code
        code = request.GET.get('code')
        # 2.通过code换取token
        qq = OAuthQQ(client_id=QQ_CLIENT_ID,
                     client_secret=QQ_CLIENT_SECRET,
                     redirect_uri=QQ_REDIRECT_URI,
                     state='None')
        token = qq.get_access_token(code)
        # 3.通过token换取openid
        openid = qq.get_open_id(token)
        # 4.根据openid进行判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 5.没有绑定过,则需要绑定
            # 加密openid
            access_token = generic_openid(openid)
            response = JsonResponse({'code':400,'access_token':access_token})
            return response
        else:
            # 6.如果绑定过,则直接登录
            # 6.1设置session
            login(request,qquser.user)
            # 6.2设置cookie
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('username',qquser.user.username)
            return response

    def post(self,request):
        data = json.loads(request.body.decode())
        password = data.get('password')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        openid = data.get('access_token')

        # 添加对access_token解密
        openid = check_access_token(openid)
        if openid is None:
            return JsonResponse({'code':400,'message':'参数缺失'})

        # 2.验证数据
        # if not all([password,mobile,sms_code,openid]):
        #     return JsonResponse({'code': 400, 'message': '参数不全'})
        #
        # # 手机号满足规则，手机号不能重复
        # if not re.match(r'^1[345789]\d{9}$', mobile):
        #     return JsonResponse({'code': 400, 'message': '手机号不满足规则'})
        #
        # # 密码满足规则
        # pwd_len = len(password)
        # if not pwd_len > 8 and pwd_len <= 20:
        #     return JsonResponse({'code': 400, 'message': '密码不满足规则'})
        #
        # # 验证短信验证码
        # redis_cli = get_redis_connection('code')
        # redis_sms_code = redis_cli.get(mobile).decode()
        # if not redis_sms_code == sms_code:
        #     return JsonResponse({'code':400,'message':'短信验证码错误'})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=mobile,
                password=password,
                mobile=mobile
            )
        else:
            if not user.check_password(password):
                return JsonResponse({'code':400,'message':'账户或密码错误'})

        OAuthQQUser.objects.create(user=user,openid=openid)

        login(request,user)

        response = JsonResponse({'code':0,'message':'ok'})
        response.set_cookie('username',user.username)

        return response