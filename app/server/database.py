import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.Connections

connections = database.get_collection("test")

def connections_helper(connection) -> dict:
    return {
        "id": str(connection["_id"]),
        "categories": connection["categories"]
    }

async def get_all_connections():
    all_connections   = []
    async for connection in connections.find():
        all_connections.append(connection)
    return all_connections

# Retrieve a student with a matching ID
async def retrieve_connections(date: str) -> dict:
    connection = await connections.find_one({"_id": date})
    if connection:
        return connections_helper(connection)

# async def add_connection(connections_data: dict) -> dict:
#     connection = await connections.insert_one(connections_data)
#     new_connection = await connections.find_one({"_id": connection.inserted_id})
#     return connections_helper(new_connection)