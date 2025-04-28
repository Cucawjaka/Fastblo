from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from src.config import settings
from src.errors.service_exeptions import InvalidTokenTypeError


auth_data = settings.auth_data
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# password
def create_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#access_token

def create_access_token(user_id: int, username: str, exp: timedelta | None = None) -> str:
    if exp is None:
        exp = timedelta(minutes=15)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": int((datetime.now(timezone.utc) + exp).timestamp()),
        "token_type": "access"
    }
    encode_jwt = jwt.encode(payload, auth_data["secret_key"], algorithm=auth_data["algorithm"])
    return encode_jwt

#refresh_token

def create_refresh_token(user_id: int, exp: timedelta | None = None) -> str:
    if exp is None:
        exp = timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "exp": int((datetime.now(timezone.utc) + exp).timestamp()),
        "token_type": "refresh"
    }
    token = jwt.encode(payload, auth_data["secret_key"], algorithm=auth_data["algorithm"])
    return token

def create_refresh_and_access_tokens(user_id: str, username: str) -> dict[str, str]:
    access_token = create_access_token(user_id=user_id, username=username)
    refresh_token = create_refresh_token(user_id=user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def verify_token(token: str) -> dict:
    try:
        data = jwt.decode(token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]])
        if not data or "sub" not in data:
            raise InvalidTokenTypeError("Неверный токен доступа")
        
        expire = data.get("exp", None)
        if expire is None:
            raise ValueError("Некорректный токен доступа")
        if datetime.now(timezone.utc).timestamp() > expire:
            raise InvalidTokenTypeError("Токен не действует")
        return data
    except JWTError:
        raise InvalidTokenTypeError("Неверный токен доступа")
    

