from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME:str = "三角洲行动陪玩店接单系统" # 项目名称
    VERSION:str = "1.0.0" # 项目版本
    API_PREFIX:str = "/api" # 所有路由的前缀
    # TODO: 未来要写上数据库的地址
    DATABASE_URL:str = "mysql+pymysql://用户名:密码@主机地址:端口号/数据库名" # 数据库链接地址
    SECRET_KEY:str = "huanxiedd_dgfhsujbvcnewiuohdsjcasldkjxcszlnkmsedijofrqwejkolpxnl" # token 签名密钥
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 60*24*7 # token有效期7天
    PLATFORM_COMMISSION: float = 0.20  # 平台抽成20%
    class Config:
        env_file = ".env"

settings = Settings()