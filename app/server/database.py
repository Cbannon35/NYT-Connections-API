import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.Connections

connections = database.get_collection("Connections")

def connections_helper(connection) -> dict:
    return {
        "id": str(connection["_id"]),
        "NYT_id": connection["NYT_id"],
        "date": connection["date"],
        "author": connection["author"],
        "answers": connection["answers"]
    }

async def retrieve_all_connections():
    all_connections   = []
    async for connection in connections.find():
        all_connections.append(connection)
    return all_connections


async def retrieve_connections_by_id(id: str) -> dict:
    connection = await connections.find_one({"_id": id})
    if connection:
        return connections_helper(connection)
    
async def retrieve_connections_by_date(date: str) -> dict:
    connection = await connections.find_one({"date": date})
    if connection:
        return connections_helper(connection)
