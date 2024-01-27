from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# Django自带一个用户模型
# 这个用户模型 有密码的加密 和密码的验证
class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name