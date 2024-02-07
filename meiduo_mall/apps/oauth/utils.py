from itsdangerous import URLSafeTimedSerializer
from meiduo_mall.settings import SECRET_KEY

# 加密
def generic_openid(openid):
    s = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    access_token = s.dumps({'openid':openid})
    return access_token

# 解密
def check_access_token(access_token):
    s = URLSafeTimedSerializer(secret_key=SECRET_KEY)

    try:
        result = s.loads(access_token,max_age=3600)
    except Exception:
        return None
    else:
        return result.get('openid')