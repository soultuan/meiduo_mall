import json
import re

from django.shortcuts import render
from django.views import View
from django.contrib.auth import login,authenticate,logout
from django.http import JsonResponse
from apps.users.models import User
from utils.views import LoginRequiredJSONMixin

from django_redis import get_redis_connection
from django.core.mail import send_mail
from apps.users.utils import generic_email_verify_token,check_email_verify_token
from celery_tasks.email.tasks import celery_send_mail

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

class LogoutView(View):
    def delete(self,request):
        logout(request)
        # 1.删除session信息
        response = JsonResponse({'code':0,'errmsg':'ok'})
        # 2.删除cookie信息，因为前端是根据cookie信息来判断用户是否登录
        response.delete_cookie('username')

        return response

# 用户中心，也必须是登录用户
# LoginRequiredMixin未登录的用户会返回重定向，重定向不是JSON数据
# 我们希望返回JSON数据，因为前后端用JSON进行交互
class CenterView(LoginRequiredJSONMixin,View):
    def get(self,request):
        info_data = {
            'username' : request.user.username,
            'mobile' : request.user.mobile,
            'email' : request.user.email,
            'email_active' :  request.user.email_active
        }
        return JsonResponse({'code':0,'errmsg':'ok','info_data':info_data})

class EmailView(LoginRequiredJSONMixin,View):
    def put(self,request):
        # 1.接收请求
        # put、post————>body
        data = json.loads(request.body.decode())
        # 2.获取数据
        email = data.get('email')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return JsonResponse({'code':400,'errmsg':'邮件格式不正确'})
        # 3.保存邮箱地址
        user = request.user
        # user/request.user就是登录用户的实例对象
        user.email = email
        user.save()
        # 4.发送一封激活邮件
        # subject
        subject = '美多商城邮箱验证'
        # message
        message = ""
        # from_email
        from_email = '17807890713@163.com'
        # recipient_list
        recipient_list = ['763302385@qq.com']
        # 4.1对a标签的连接数据进行加密处理
        # 用user_id来认证邮箱
        token = generic_email_verify_token(request.user.id)
        verify_url = f"http://www.meiduo.site:8080/success_verify_email.html?token={token}"
        # 组织我们的激活邮件
        # html_message
        html_message = '<p>尊敬的用户您好！</p>'\
                        '<p>感谢您使用美多商城。</p>'\
                        f'<p>您的邮箱为:{email}</p>'\
                        f'<p><a href="{verify_url}">{verify_url}<a></p>'

        celery_send_mail.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
            )
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message
        #           )
        # 5.返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})

class EmailVerifyView(View):
    def put(self,request):
        # 1.接收参数
        params = request.GET
        # 2.获取参数
        token = params.get('token')
        # 3.验证参数
        if token is None:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        # 4.获取user_id
        user_id = check_email_verify_token(token)
        if user_id is None:
            return JsonResponse({'code':400,'errmsg':'参数错误'})
        # 5.根据用户id查询数据
        user = User.objects.get(id=user_id)
        # 6.修改数据
        user.email_active = True
        user.save()
        # 7.返回响应
        return JsonResponse({'code':0,'errmsg':'ok'})
