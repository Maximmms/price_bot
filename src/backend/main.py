from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.backend.routers.users import users_router
from src.backend.routers.vendors import vendor_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Price Checker API",
    description="API to check the price of a product",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Mount static files for web frontend
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent  # Корень проекта (PriceBot/)
WEBSITE_DIR = PROJECT_DIR / "src" / "frontend" / "website"

if not WEBSITE_DIR.exists():
    raise FileNotFoundError(f"Директория с фронтендом не найдена: {WEBSITE_DIR}")

app.mount("/web", StaticFiles(directory=str(WEBSITE_DIR), html=True), name="website")

app.include_router(users_router, prefix="/api/v1")
app.include_router(vendor_router, prefix="/api/v1")


@app.get("/", response_class=RedirectResponse)
async def redirect_to_web():
    """Redirect root URL to web interface"""
    return "/web/"


@app.get("/health")
def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "Price Checker API is running"
        },
        status_code=200
    )


@app.get("/api/v1/")
def read_root():
    return JSONResponse(
        content={
            "message": "Welcome to the Price Checker API!",
            "status": "success"
        },
        status_code=200
    )
