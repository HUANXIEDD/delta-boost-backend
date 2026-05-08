from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.dependencies import get_current_booster
from app.models import Booster, BoosterPrice, Order, Review
from app.schemas.booster import (
    BoosterCreate, BoosterLogin, BoosterUpdate, BoosterResponse
)
from app.schemas.booster_price import BoosterPriceCreate, BoosterPriceResponse, BoosterPriceUpdate
from app.core.security import verify_password, get_password_hash, create_access_token


def generate_booster_unique_id(db: Session) -> str:
    latest = db.query(Booster).order_by(Booster.id.desc()).first()
    if latest:
        num = int(latest.unique_id[3:]) + 1
    else:
        num = 1
    return f"BST{num:03d}"
router = APIRouter(prefix="/booster", tags=["打手"])

@router.post("/register" , status_code = status.HTTP_201_CREATED)
def register_boosters(data : BoosterCreate , db : Session = Depends(get_db)):
    print(f"[info]注册接口被调用，注册信息：{data}")
    existing = db.query(Booster).filter(Booster.username == data.username).first()
    if existing :
        raise HTTPException(status_code = 400 , detail = "此打手已经存在")
    hashed = get_password_hash(data.password)
    booster = Booster(username = data.username , password_hash = hashed , unique_id = generate_booster_unique_id(db))
    db.add(booster)
    db.commit()
    db.refresh(booster)
    return {"message" : "注册成功" , "booster_id" : booster.id}

@router.post("/login" , status_code = status.HTTP_200_OK)
def login_boosters(data : BoosterLogin , db : Session = Depends(get_db)):
    print(f"[info]登陆接口被调用，登陆信息：{data}")
    booster = db.query(Booster).filter(Booster.username == data.username).first()
    if not booster:
        raise HTTPException(status_code = 401 , detail = "用户名或密码错误")
    if not verify_password(data.password , booster.password_hash):
        raise HTTPException(status_code = 401 , detail = "用户名或密码错误")
    token = create_access_token({"sub" : booster.username , "role" : "booster"})

    return {"access_token" : token , "token_type" : "bearer"}

@router.post("/profile" , status_code = status.HTTP_201_CREATED)
def profile(data : BoosterUpdate ,
            db : Session = Depends(get_db),
            current_booster : Booster = Depends(get_current_booster)):
    if data.avatar is not None:
        current_booster.avatar = data.avatar
    if data.bio is not None:
        current_booster.bio = data.bio
    if data.services is not None:
        current_booster.services = data.services
    db.commit()
    db.refresh(current_booster)
    return{"message":"更新成功" , "booster" : current_booster}

@router.get("/profile" , status_code = status.HTTP_200_OK)
def get_profile(current_booster : Booster = Depends(get_current_booster)):
    return current_booster

@router.get("/price" , status_code = status.HTTP_200_OK)
def get_price(current_booster : Booster = Depends(get_current_booster)):
    return current_booster.prices

@router.post("/updateprice" , status_code = status.HTTP_201_CREATED)
def update_price(data : BoosterPriceUpdate ,
                 db : Session = Depends(get_db),
                 current_booster : Booster = Depends(get_current_booster)):
    if data.price is not None:
        current_booster.price = data.price
    db.commit()
    db.refresh(current_booster)
    return {"message" : "更新成功" , "price" : current_booster.price}