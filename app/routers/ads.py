
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ad, Category, User
from app.schemas import AdCreate, AdUpdate, AdResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api/ads",
    tags=["Объявления"]
)


# Общая лента объявлений
@router.get("/", response_model=list[AdResponse])
def get_ads(
    q: str | None = None,
    category_id: int | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    sort: str = "newest",
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = select(Ad).where(Ad.is_active == True)

    # Поиск по названию и описанию
    if q:
        statement = statement.where(
            or_(
                Ad.title.ilike(f"%{q}%"),
                Ad.description.ilike(f"%{q}%")
            )
        )

    # Фильтр по категории
    if category_id is not None:
        statement = statement.where(Ad.category_id == category_id)

    # Фильтр по цене
    if min_price is not None:
        statement = statement.where(Ad.price >= min_price)

    if max_price is not None:
        statement = statement.where(Ad.price <= max_price)

    # Сортировка
    if sort == "newest":
        statement = statement.order_by(Ad.created_at.desc())
    elif sort == "oldest":
        statement = statement.order_by(Ad.created_at.asc())
    elif sort == "price_asc":
        statement = statement.order_by(Ad.price.asc())
    elif sort == "price_desc":
        statement = statement.order_by(Ad.price.desc())
    else:
        raise HTTPException(status_code=422, detail="Неверный параметр сортировки")

    # Пагинация
    statement = statement.limit(limit).offset(offset)

    return db.scalars(statement).all()


# Мои объявления
@router.get("/mine", response_model=list[AdResponse])
def get_my_ads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    statement = (
        select(Ad)
        .where(Ad.user_id == current_user.id)
        .order_by(Ad.created_at.desc())
    )

    return db.scalars(statement).all()


# Статистика объявлений
@router.get("/stats/summary")
def get_ads_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(
        select(
            func.count(Ad.id),
            func.sum(Ad.price),
            func.avg(Ad.price)
        ).where(Ad.is_active == True)
    ).one()

    return {
        "total_ads": result[0] or 0,
        "total_price": round(result[1] or 0, 2),
        "average_price": round(result[2] or 0, 2)
    }


# Статистика по категориям
@router.get("/stats/categories")
def get_category_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(
        select(
            Category.name,
            func.count(Ad.id),
            func.avg(Ad.price)
        )
        .outerjoin(Ad, Category.id == Ad.category_id)
        .group_by(Category.id, Category.name)
        .order_by(Category.name)
    ).all()

    return [
        {
            "category": row[0],
            "ads_count": row[1],
            "average_price": round(row[2] or 0, 2)
        }
        for row in result
    ]


# Получение одного объявления
@router.get("/{ad_id}", response_model=AdResponse)
def get_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad = db.get(Ad, ad_id)

    if ad is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    return ad


# Создание объявления
@router.post("/", response_model=AdResponse, status_code=201)
def create_ad(
    data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.get(Category, data.category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    ad = Ad(
        title=data.title,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        user_id=current_user.id
    )

    db.add(ad)
    db.commit()
    db.refresh(ad)

    return ad


# Редактирование своего объявления
@router.put("/{ad_id}", response_model=AdResponse)
def update_ad(
    ad_id: int,
    data: AdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad = db.get(Ad, ad_id)

    if ad is None or ad.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"Поле {field} не может быть пустым"
            )

    if "category_id" in changes:
        category = db.get(Category, changes["category_id"])

        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")

    for field, value in changes.items():
        setattr(ad, field, value)

    db.commit()
    db.refresh(ad)

    return ad


# Удаление своего объявления
@router.delete("/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad = db.get(Ad, ad_id)

    if ad is None or ad.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    db.delete(ad)
    db.commit()

    return {"message": "Объявление успешно удалено"}
