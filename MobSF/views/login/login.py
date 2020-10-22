import json

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views import View

# 登陆接口
from MobSF.models import User
from MobSF.views.login.utils import generate_jwt, get_user_by_token


class LoginView(View):
    '''登陆'''

    def post(self, request):
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        user_item = User.objects.filter(username=username)
        if len(user_item) == 1:
            ret = user_item[0].check_password(password)
            if ret:
                token = generate_jwt(user_item[0].id)
                return JsonResponse({'errmsg': 'ok', 'code': 0, 'token': token})
            else:
                return JsonResponse({'errmsg': '密码错误', 'code': 201})
        else:
            return JsonResponse({'errmsg': '用户不存在', 'code': 201})


class VerifyView(View):
    '''校验是否登录'''

    def get(self, request):
        user = get_user_by_token(request)
        if user:
            return JsonResponse({'errmsg': 'ok', 'code': 0})
        else:
            return JsonResponse({"errmsg": 'error', 'code': 201})


# 检验用户名是否已存在
class VerifyUserNameView(View):
    def post(self, request):
        username = json.loads(request.body.decode()).get('username')
        user = User.objects.filter(username=username)
        if len(user) != 0:
            return JsonResponse({'errmsg': '用户名已存在', 'code': 1})
        else:
            return JsonResponse({'errmsg': 'ok', 'code': 0})
