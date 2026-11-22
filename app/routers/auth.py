
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import register_user, authenticate_user
from app.schemas import RegisterRequest, LoginRequest, UserResponse


router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


# Регистрация
@router.post("/register", response_model=UserResponse)
def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = register_user(db, data.username, data.password)

    if user is None:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким именем уже существует"
        )

    request.session["user_id"] = user.id

    return user


# Вход
@router.post("/login", response_model=UserResponse)
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, data.username, data.password)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )

    request.session["user_id"] = user.id

    return user


# Выход
@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Вы вышли из аккаунта"}


# Проверка текущего пользователя
@router.get("/me", response_model=UserResponse)
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Необходимо войти в аккаунт"
        )

    from app.models import User

    user = db.get(User, user_id)

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден"
        )

    return user
