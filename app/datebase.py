from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

Session = sessionmaker (autocommit=False , autoflush=False , bind = engine)

Base = declarative_base()

def get_db():
    """
    获取数据库会话

    每次请求调用一次，自动打开，用完自动关闭
    用法：在路由函数参数里写 db ：Session = depends(get_db)
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()