# Refactored to app.py for slowapi

# from fastapi import APIRouter, Body
# from fastapi.encoders import jsonable_encoder

# from app.server.database import (
#     get_all_connections,
#     retrieve_connections,
# )
# from app.server.models.connections import (
#     ErrorResponseModel,
#     ResponseModel,
#     Category,
#     Connections,
# )

# router = APIRouter()

# # @router.post("/", response_description="Connections data added into the database")
# # async def add_connections(connections: Connections = Body(...)):
# #     connections = jsonable_encoder(connections)
# #     new_student = await add_student(student)
# #     return ResponseModel(new_student, "Student added successfully.")

# @router.get("/", response_description="Students retrieved")
# async def get_connections():
#     connections = await get_all_connections()
#     if connections:
#         return ResponseModel(connections, "Data retrieved successfully")
#     return ResponseModel(connections, "Empty list returned")


# @router.get("/{date}", response_description="Student data retrieved")
# async def get_student_data(date):
#     student = await retrieve_connections(date)
#     if student:
#         return ResponseModel(student, "Student data retrieved successfully")
#     return ErrorResponseModel("An error occurred.", 404, "Student doesn't exist.")