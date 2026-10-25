from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

import secrets
import hashlib





def create_access_token(sub: str, role: str, expires_delta: timedelta | None = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    
    payload = {"sub": sub, "role": role, "exp": expire}
    
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    
    return encoded_jwt




def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token):
    try:
        decoded_jwt = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        
        return decoded_jwt
    except jwt.InvalidTokenError:
        return None