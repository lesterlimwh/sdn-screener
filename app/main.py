from fastapi import FastAPI
from app.routes import screener

app = FastAPI()

app.include_router(screener.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return { "message": "OFAC SDN Screener Service" }
