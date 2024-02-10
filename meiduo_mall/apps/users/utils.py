from itsdangerous import URLSafeTimedSerializer
from meiduo_mall.settings import SECRET_KEY

def generic_email_verify_token(user_id):
    s = URLSafeTimedSerializer(secret_key=SECRET_KEY)
    data = s.dumps(user_id)
    return data