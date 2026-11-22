
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api/categories",
    tags=["Категории"]
)


# Получение списка категорий
@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.scalars(
        select(Category).order_by(Category.name)
    ).all()


# Создание категории
@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.scalar(
        select(Category).where(Category.name == data.name)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Такая категория уже существует"
        )

    category = Category(name=data.name)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# Удаление категории
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Категория не найдена"
        )

    if category.ads:
        raise HTTPException(
            status_code=409,
            detail="Нельзя удалить категорию, в которой есть объявления"
        )

    db.delete(category)
    db.commit()

    return {"message": "Категория успешно удалена"}
