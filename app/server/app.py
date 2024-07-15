from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime

# from app.server.routes.connections import router as ConnectionsRouter
# app.include_router(ConnectionsRouter, tags=["Connections"], prefix="/connections")

from .database import (
    retrieve_connections_by_date,
    retrieve_connections_by_id,
)
from .models.connections import (
    ErrorResponseModel,
    ResponseModel,
    Category,
    Connections,
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>NYT Connections API</title>
        </head>
        <body>
            <h1>Welcome!</h1>
            <h2>NYT Connections API</h2>
            <p>This is an unofficial API for the New York Times Connections game. It scrapes the daily Connections game and stores the data in a MongoDB database.</p>
            <p>Endpoints:</p>
            <ul>
                <li><a href="/connections/">/connections/</a> - Retrieve the connections data for today</li>
                <li><a href="/connections/2024-04-28">/connections/{date}</a> - Retrieve the connections data for a specific date</li>
            </ul>
            <p>Documentation:</p>
            <ul>
                <li><a href="/docs">/docs</a> - FastAPI auto-generated documentation</li>
                <li><a href="/redoc">/redoc</a> - FastAPI auto-generated documentation (redoc)</li>
            </ul>
        </body>
    </html>
    """

@app.get("/connections/", response_description="Daily Connections retrieved")
@limiter.limit("1/second")
async def get_daily_connections(request: Request):
    current_date = datetime.now()
    connection = await retrieve_connections_by_date(current_date.strftime('%Y-%m-%d'))
    if connection:
        return ResponseModel(connection, "Data retrieved successfully")
    return ResponseModel(connection, "Empty list returned")

# @app.get("/connections/all", response_description="Connections retrieved")
# @limiter.limit("1/second")
# async def get_connections(request: Request):
#     connections = await retrieve_all_connections()
#     if connections:
#         return ResponseModel(connections, "Data retrieved successfully")
#     return ResponseModel(connections, "Empty list returned")

@app.get("/connections/{date}", response_description="Connections retrieved at a specific date")
@limiter.limit("1/second")
async def get_student_data(date, request: Request):
    connection = await retrieve_connections_by_date(date)
    if connection:
        return ResponseModel(connection, "Connections data retrieved successfully from " + date)
    return ErrorResponseModel("An error occurred.", 404, "Invalid date format or Connections data doesn't exist for that date.")