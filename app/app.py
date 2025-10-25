from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.routers import router as houses_router
from src import config

app = FastAPI(
    title="Tech Challenge API",
    description="API for the Tech Challenge",
    version="1.0.0",
)


TEMPLATES_DIR = config.BASE_DIR / "template"             
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

app.include_router(houses_router)
