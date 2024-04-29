from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# from app.server.routes.connections import router as ConnectionsRouter
# app.include_router(ConnectionsRouter, tags=["Connections"], prefix="/connections")

from app.server.database import (
    get_all_connections,
    retrieve_connections,
)
from app.server.models.connections import (
    ErrorResponseModel,
    ResponseModel,
    Category,
    Connections,
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Connections API. Navigate to /connections to retrieve connections data."}

@app.get("/connections/", response_description="Connections retrieved")
@limiter.limit("1/second")
async def get_connections(request: Request):
    connections = await get_all_connections()
    if connections:
        return ResponseModel(connections, "Data retrieved successfully")
    return ResponseModel(connections, "Empty list returned")


@app.get("/connections/{date}", response_description="Connections retrieved at a specific date")
@limiter.limit("1/second")
async def get_student_data(date, request: Request):
    student = await retrieve_connections(date)
    if student:
        return ResponseModel(student, "Connections data retrieved successfully from " + date)
    return ErrorResponseModel("An error occurred.", 404, "Invalid date format or Connections data doesn't exist for that date.")