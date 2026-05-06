from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# 创建密码哈希工具，使用 bcrypt 算法 版本自动
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """"
    验证密码是否匹配。

    Args：
        plain_password : 用户明文传输的密码
        hashed_password: 数据库里存储的哈希密码
    Returns:
        密码匹配返回 True , 否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    将明文密码转为哈希密
    Args:
        password:用户输入的明文密码。
    Return：
        哈希后的密码字符串
    """
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
     创建 JWT Token
    Args:
        data: 要存入 Token 的数据，格式 {"sub": 用户名, "role": 角色}
    Return:
        签发后的JWT字符串
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": data["sub"], "role": data["role"], "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    验证JWT Token 是否有效

    Args:
        token: 客户端传来的JWT Token
    Return:
        有效则返回 {"sub": 用户名, "role": 角色}，无效则返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {"sub": payload.get("sub"), "role": payload.get("role")}
    except JWTError:
        return None
