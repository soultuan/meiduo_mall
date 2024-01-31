from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from django_redis import get_redis_connection
from django.http import HttpResponse,JsonResponse
from random import randint

# Create your views here.
class ImageCodeView(View):

    def get(self,request,uuid):
        # 1.接收路由中的uuid
        # 2.生成图片验证码和图片二进制
        # text是图片验证码的内容，例如：xyzz
        # image是图片二进制
        text,image = captcha.generate_captcha()
        # 3.通过redis把图片验证码保存起来
        # 3.1进行redis的连接
        redis_cli = get_redis_connection('code')
        # 3.2指令操作
        # name,time,value
        redis_cli.setex(uuid,100,text)
        # 4.返回图片二进制
        # 因为图片是二进制，我们不能返回json数据
        # content_type=响应体数据类型
        # content_type的语法形式：大类/小类
        # content_type（MIME类型）
        # 图片：image/jpeg,image/gif,image/png
        return HttpResponse(image,content_type='image/jpeg')

class SmsCodeView(View):

    def get(self,request,mobile):
        # 1.获取请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2.验证参数
        if not all([image_code,uuid]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})
        # 3.验证图片验证码
        # 3.1连接redis
        redis_cli = get_redis_connection('code')
        # 3.2获取redis数据,redis中的数据以二进制形式存储，所以需要decode()
        if redis_cli.get(uuid) is None:
            return JsonResponse({'code':400,'errmsg':'图片验证码失效'})
        redis_image_code = redis_cli.get(uuid).decode().lower()
        image_code = image_code.lower()
        # 3.3对比
        if redis_image_code != image_code:
            return JsonResponse({'code':400,'errmsg':'图片验证码错误'})

        if redis_cli.get('send_flag_%s'%mobile) is not None:
            return JsonResponse({'code':400,'errmsg':'操作过于频繁，请稍后再试'})
        # 4.生成短信验证码
        sms_code = '%04d' % randint(0,9999)
        # 5.保存短信验证码
        redis_cli.setex(mobile,300,sms_code)
        # 添加一个发送标记，有效期是60s，避免频繁发送请求
        redis_cli.setex('send_flag_%s'%mobile,60,1)
        # 6.发送短信验证码
        ccp = CCP()
        ccp.send_template_sms(mobile,[sms_code, 5],1)
        # 7.返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})