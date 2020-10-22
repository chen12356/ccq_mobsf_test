# 访问限制
from MobSF.models import User
from MobSF.settings import SECRET_KEY


class Astrict():
    pass


# token
import datetime
import jwt


def generate_jwt(user_id):
    '''生成jwt'''
    payload = {
        'exp': datetime.datetime.now() + datetime.timedelta(days=1),  # 过期时间
        'data': {"user_id": user_id}
    }
    token = jwt.encode(payload, SECRET_KEY).decode()
    return token


def verify_jwt(token):
    '''token校验'''
    try:
        data = jwt.decode(token, SECRET_KEY)
    except Exception as e:
        return None
    return data


def get_user_by_token(request):
    '''通过token获取对应的用户对象'''
    token = get_token(request)
    data = verify_jwt(token)
    if data:
        try:
            user_id = data.get('data').get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except Exception as e:
            return None
    else:
        return None


def get_token(request):
    '''从请求头中获取token'''
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    return token
