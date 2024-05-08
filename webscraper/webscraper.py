# Adapted from https://github.com/Eyefyre/NYT-Connections-Answers/tree/main to add to MongoDB database

import motor.motor_asyncio
from decouple import config
import asyncio
import json
from datetime import datetime, timedelta  
import requests

today = datetime.today()
MONGO_DETAILS = config("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.Connections
connections_database = database.get_collection("Connections")

async def get_last_id():
    # TODO: know the start date so instead of sorting db, we can do math
    last_document = await connections_database.find_one(sort=[("_id", -1)])
    return last_document["_id"]

def get_connections(date, last_id) -> dict:
    URL = f"https://www.nytimes.com/svc/connections/v1/{date}.json" 
    r = requests.get(URL)

    content = json.loads(r.content)
    id = content["id"]
    print(f"Adding Connections #{id} from {date}")
    groups = []
    for group in content["groups"]:
        categ = {"level":content["groups"][group]["level"],"group":group,"members":content["groups"][group]["members"]}
        groups.append(categ)

    con_item = {"_id": int(last_id+1), "NYT_id": int(id), "date":date,"author": "NYT","answers": groups}
    # print(con_item)
    return con_item

async def insert_document(data, db):
    try:
        result = await db.insert_one(data)
        print(f"Inserted document with ID: {result.inserted_id}")
    except Exception as e:
        # Guarding against duplicate keys
        print(e)

async def main():
    last_id = await get_last_id()
    # print(last_id)
    con_item = get_connections(today.strftime('%Y-%m-%d'), last_id)
    # print(con_item)
    await insert_document(con_item, connections_database)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# Used to populate my database with all connections from the epoch date to today
# async def add_all_connections():
#     starting_id = 0
#     epoch_date = datetime(2023, 6, 12)
#     date_pointer = epoch_date
#     while date_pointer <= today:
#         con_item = get_connections(date_pointer.strftime('%Y-%m-%d'), starting_id)
#         await insert_document(con_item, connections_database)
#         date_pointer += timedelta(days=1)
#         starting_id += 1
        