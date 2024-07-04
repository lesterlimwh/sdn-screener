from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_redis_rate_limiter import RedisRateLimiterMiddleware, RedisClient
from app.routes import screener


app = FastAPI()

app.include_router(screener.router, prefix="/api/v1")

# Initialize the Redis client
redis_client = RedisClient(host="localhost", port=6379, db=0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Apply the rate limiter middleware to the app
app.add_middleware(
    RedisRateLimiterMiddleware,
    redis_client=redis_client,
    limit=40,
    window=60
)

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/")
def read_root():
    return { "message": "OFAC SDN Screener Service" }
