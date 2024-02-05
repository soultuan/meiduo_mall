from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.settings import QQ_CLIENT_ID,QQ_CLIENT_SECRET,QQ_REDIRECT_URI
from django.http import JsonResponse
from apps.oauth.models import OAuthQQUser
from django.contrib.auth import login
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
            response = JsonResponse({'code':400,'access_token':openid})
            return response
        else:
            # 6.如果绑定过,则直接登录
            # 6.1设置session
            login(request,qquser.user)
            # 6.2设置cookie
            response = JsonResponse({'code':0,'errmsg':'ok'})
            response.set_cookie('username',qquser.user.username)
            return response
        pass