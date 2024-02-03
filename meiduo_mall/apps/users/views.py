import json
import re

from django.shortcuts import render
from django.views import View
from django.contrib.auth import login,authenticate
from django.http import JsonResponse
from apps.users.models import User

from django_redis import get_redis_connection

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

class  UsermobileCountView(View):

    def get(self,request,mobile):
        # 1.接收用户名，对这个用户名进行判断
        # if not re.match('[a-zA-Z0-9_-]{5,20}',username):
        #     return JsonResponse({'code':200,'errmsg':'用户名不满足规范'})
        # 2.根据手机号查询数据库
        count = User.objects.filter(mobile=mobile).count()
        # 3.返回响应
        return JsonResponse({'code':0,'count':count,'errmsg':'ok'})


class RegisterView(View):

    def post(self,request):
        # 1.接受请求（POST-------JSON）
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)
        # 2.获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        sms_code = body_dict.get('sms_code')
        allow = body_dict.get('allow')
        # 3.验证数据
        #     3.1用户名、密码、确认密码、手机号、是否同意协议都要有# 参数名称与对应的变量
        params = {
            '用户名': username,
            '密码': password,
            '确认密码': password2,
            '手机号': mobile,
            '是否同意协议': allow,
        }
        #
        #     # 检查参数是否完整
        missing_params = [name for name, value in params.items() if not value]
        if missing_params:
            return JsonResponse({'code': 400, 'errmsg': f'{",".join(missing_params)} 参数缺失'})
        # if not all([username,password,password2,mobile,allow]):
        #     return JsonResponse({'code':400,'errmsg':'参数不全'})
        #     3.2用户名满足协议、用户名不能重复
        if not re.match('[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':400,'errmsg':'用户名不满足规则'})
        #     3.3密码满足规则
        pwd_len = len(password)
        if not pwd_len > 8 and pwd_len <= 20:
            return JsonResponse({'code':400,'errmsg':'密码不满足规则'})

        #     3.4确认密码和密码一致
        if not password == password2:
            return JsonResponse({'code':400,'errmsg':'两次密码不一致'})

        #     3.5手机号满足规则，手机号不能重复
        if not re.match(r'^1[345789]\d{9}$',mobile):
            return JsonResponse({'code':400,'errmsg':'手机号不满足规则'})

        # 验证短信验证码
        redis_cli = get_redis_connection('code')
        redis_sms_code = redis_cli.get(mobile).decode()
        if not redis_sms_code == sms_code:
            return JsonResponse({'code':400,'errmsg':'短信验证码错误'})

        #     3.6需要同意协议
        if not allow:
            return JsonResponse({'code':400,'errmsg':'用户未同意协议'})

        # 4.数据入库
        # User.objects.create(
        #     username = username,
        #     password = password,
        #     mobile = mobile
        # )
        # 调用这个create_user方法可以实现密码加密
        user = User.objects.create_user(
            username= username,
            password = password,
            mobile = mobile
        )

        # 系统(Django)为我们提供了状态保持的方法
        # request,user,
        # 状态保持--登录用户的状态保持
        # user已经登录的用户信息
        login(request,user)
        # 5.返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})

class LoginView(View):

    def post(self,request):
        # 1.接收数据
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 2.验证数据
        if not all([username,password]):
            return JsonResponse({'code':400,'errmsg':'参数不全'})

        # 确定我们是根据手机号还是用户名查询
        # USERNAME_FIELD 我们可以根据修改User.USERNAME_FIELD字段
        # 来影响authenticate的查询
        # authenticate就是根据USERNAME_FIELD来查询
        if re.match(r'1[345789]\d{9}',username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 3.验证用户名和密码是否正确
        # 3.1查询数据库来验证
        # 3.2使用django的authenticate传递用户名和密码
        user = authenticate(username=username,password=password)
        # 如果用户名和密码正确，则返回User信息，
        # 如果用户名和密码不正确，则返回None
        if user is None:
            return JsonResponse({'code':400,'errmsg':'用户名或密码错误'})
        # 4.session
        login(request,user)
        # 5.判断是否记住登录
        if remembered:
            # 记住登录，默认两周
            request.session.set_expiry(None)
        else:
            # 不记住登录，浏览器关闭session过期
            request.session.set_expiry(0)
        # 6.返回响应
        response = JsonResponse({'code':0,'errmsg':'ok'})
        # 为了首页显示用户信息
        response.set_cookie('username',username)
        return response