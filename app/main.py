
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import FileResponse

from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.ads import router as ads_router
app = FastAPI(
    title="Доска объявлений",
    description="Учебный проект — вариант 16",
    version="1.0.0"
)

# Подключение сессий пользователей
app.add_middleware(
    
    SessionMiddleware,
    secret_key="change-this-secret-key-before-deployment"
)

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(ads_router)
# Подключение CSS, JavaScript и других статических файлов
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Сервер работает!"}

# Главная страница
@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse("app/templates/index.html")


# Страница входа
@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse("app/templates/login.html")


# Страница регистрации
@app.get("/register", include_in_schema=False)
def register_page():
    return FileResponse("app/templates/register.html")


# Мои объявления
@app.get("/my-ads", include_in_schema=False)
def my_ads_page():
    return FileResponse("app/templates/index.html")