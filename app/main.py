from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.database import Base, engine
from app.routers import booster_router, customer_router, reservation_router, shop_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时创建所有数据库表，关闭时不做处理"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# 注册路由
app.include_router(shop_router, prefix=settings.API_PREFIX)
app.include_router(booster_router, prefix=settings.API_PREFIX)
app.include_router(customer_router, prefix=settings.API_PREFIX)
app.include_router(reservation_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {"message": "三角洲行动陪玩店接单系统", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
