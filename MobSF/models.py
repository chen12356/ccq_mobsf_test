# 用户模型
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=100,verbose_name='密码')
    is_active = models.IntegerField(default=1, null=True)  # 活动账号
    is_staff = models.IntegerField(default=0, null=True)
    is_superuser = models.IntegerField(default=0, null=True)

    class Meta:
        db_table = "t_user"
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser
        }
