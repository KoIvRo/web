import jwt
from django.conf import settings
from django.utils import timezone

def create_access_token(user_id: int):
    payload = {
        "user_id": user_id,
        "type": "access",
        "exp": timezone.now() + settings.JWT_ACCESS_LIFETIME,
        "iat": timezone.now()
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: int):
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": timezone.now() + settings.JWT_REFRESH_LIFETIME,
        "iat": timezone.now()
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception as e:
        return None
    
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        new_access_token = create_access_token(payload["user_id"])
        return new_access_token
    except Exception as e:
        print(e)
        return None