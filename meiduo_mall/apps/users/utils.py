from itsdangerous import URLSafeTimedSerializer
from meiduo_mall.settings import SECRET_KEY

def generic_email_verify_token(user_id):
    s = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    data = s.dumps({'user_id':user_id})
    return data

def check_email_verify_token(token):
    s = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    try:
        result = s.loads(token,max_age=3600*24)
    except Exception:
        return None
    else:
        return result.get('user_id')