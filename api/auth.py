from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "KEY"
ALGORITHM = "HS256"

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except (ExpiredSignatureError, InvalidTokenError):
        return None


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def dispatch(self, request: Request, call_next):
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

        if not access_token:
            access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Missing token")

        payload = verify_jwt(access_token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        request.state.user = payload
        return call_next(request)