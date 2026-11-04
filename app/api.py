from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.service import AssistantService
from app.config import load_config

cfg = load_config()
app = FastAPI(title=cfg.get("app", "name", default="shop-assistant"))

# CORS: в проде заменить "*" на домен магазина
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

svc = AssistantService(cfg)

# Папка со статикой виджета (widget.js, widget.css, demo.html)
WIDGET_DIR = Path(__file__).resolve().parent / "static"


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    source: str
    intent: str | None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    source: str
    intent: str | None


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    return AskResponse(**svc.ask(req.question))


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Эндпоинт для веб-виджета на сайте магазина."""
    return ChatResponse(**svc.ask(req.message))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/demo")
def demo_page():
    return FileResponse(WIDGET_DIR / "demo.html", media_type="text/html")


@app.get("/widget.js")
def widget_js():
    return FileResponse(
        WIDGET_DIR / "widget.js",
        media_type="application/javascript",
    )


@app.get("/widget.css")
def widget_css():
    return FileResponse(WIDGET_DIR / "widget.css", media_type="text/css")