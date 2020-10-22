'''修改密码'''
import json
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from MobSF.models import User
from MobSF.views.login.utils import get_user_by_token


# 自定义管理员新增用户
class XadminAddUserView(View):
    def get(self, request):
        template = 'admin/admin.html'
        return render(request, template)

    def post(self, request):
        dict = request.POST
        username = dict.get('username')
        password1 = dict.get('password1')
        password2 = dict.get('password2')
        user = User.objects.filter(username=username)
        if len(user) == 1:
            return JsonResponse({'errmsg': '用户名已存在', 'code': 201})
        if password1 != password2:
            return JsonResponse({'errmsg': '密码输入不一致', 'code': 200})
        User.objects.create_user(username=username, password=password1)
        template = 'admin/allUser.html'
        return render(request, template)


# 管理员修改用户密码
class XadminRePwdView(View):
    def get(self, request, user_id):
        template = 'general/xadmin_repwd.html'
        return render(request, template)

    def post(self, request, user_id):
        user = User.objects.filter(id=user_id)
        if len(user) == 0:
            return JsonResponse({'errmsg': '用户不存在', 'code': 201})
        user = user[0]
        dict = json.loads(request.body.decode())
        new_pwd = dict.get('new_pwd')
        new_pwd2 = dict.get('sure_pwd')
        if new_pwd != new_pwd2:
            return JsonResponse({'errmsg': '密码不一致', 'code': 202})
        if new_pwd and new_pwd2:
            user.set_password(raw_password=new_pwd)
            user.save()
            return JsonResponse({'errmsg': 'ok', 'code': 0, 'user_id': user_id})
        else:
            return JsonResponse({'errmsg': '密码为空', 'code': 400})


# 用户修改密码,需要提供旧密码
class RePwdView(View):
    def get(self, request):
        template = 'general/repwd.html'
        return render(request, template)

    def post(self, request):
        user = get_user_by_token(request)
        if not user:
            return JsonResponse({'errmsg': '用户不存在', 'code': 201})
        dict = json.loads(request.body.decode())
        old_pwd = dict.get('old_pwd')
        new_pwd = dict.get('new_pwd')
        new_pwd2 = dict.get('sure_pwd')
        if new_pwd != new_pwd2:
            return JsonResponse({'errmsg': '密码不一致', 'code': 202})
        ret = user.check_password(raw_password=old_pwd)
        if not ret:
            return JsonResponse({'errmsg': '旧密码错误', 'code': 203})
        if new_pwd == old_pwd:
            return JsonResponse({'errmsg': '新密码不能与旧密码一致', 'code': 204})
        user.set_password(raw_password=new_pwd)
        user.save()
        return JsonResponse({'errmsg': 'ok', 'code': 0})
