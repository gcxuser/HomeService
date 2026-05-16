from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from HomeService.api import chat, appointment, catalog, workers, knowledge, auth, users, orders, admin, mcp
from HomeService.db.seed import seed_default_data
from HomeService.db.session import init_db
from HomeService.services.knowledge_service import KnowledgeService
from HomeService.utils.exceptions import HomeServiceException

app = FastAPI(title="HomeService AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(appointment.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["catalog"])
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def root():
    """重定向到静态页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/")

@app.on_event("startup")
async def startup_event():
    init_db()
    seed_default_data()
    KnowledgeService()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.exception_handler(HomeServiceException)
async def home_service_exception_handler(
    request: Request,
    exc: HomeServiceException,
):
    """Custom exception handler for HomeServiceException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "detail": exc.detail,
                "headers": exc.headers,
            }
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "detail": "An internal error occurred. Please try again later.",
            }
        },
    )
