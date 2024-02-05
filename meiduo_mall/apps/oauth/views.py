from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.settings import QQ_CLIENT_ID,QQ_CLIENT_SECRET,QQ_REDIRECT_URI
from django.http import JsonResponse
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