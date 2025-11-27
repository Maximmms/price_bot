from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.backend.routers.users import users_router

app = FastAPI(
    title="Price Checker API",
    description="API to check the price of a product",
    version="1.0.0",
    root_path="/api/v1",
    root_path_in_servers=False,
)
app.servers = [{"url": "/api/v1", "description": "API Server"}]

app.include_router(users_router)

@app.get("/")
def read_root():
    return JSONResponse(
        content={
            "message": "Welcome to the Price Checker API!",
            "status": "success"
        },
        status_code=200
    )