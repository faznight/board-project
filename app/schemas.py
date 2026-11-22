
from pydantic import BaseModel, Field


# Данные для регистрации
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# Данные для входа
class LoginRequest(BaseModel):
    username: str
    password: str


# Информация о пользователе
class UserResponse(BaseModel):
    id: int
    username: str


# Создание категории
class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


# Информация о категории
class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# Создание объявления
class AdCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5, max_length=2000)
    price: float = Field(ge=0)
    category_id: int


# Обновление объявления
class AdUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    price: float | None = Field(default=None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None


# Информация об объявлении
class AdResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    is_active: bool
    user_id: int
    category_id: int

    model_config = {"from_attributes": True}
