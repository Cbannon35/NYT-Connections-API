from fastapi import FastAPI

from app.server.routes.connections import router as ConnectionsRouter

app = FastAPI()

app.include_router(ConnectionsRouter, tags=["Connections"], prefix="/connections")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}