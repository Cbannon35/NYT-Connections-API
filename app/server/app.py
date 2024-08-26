from fastapi import Body, FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

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
app = FastAPI(
    title="Connections API",
    summary="Retrieve data from the New York Times Connections game. Endpoints allow creating a clone of the game.",
    version="0.0.1",
    contact={
        "name": "Christopher Bannon",
    },
)
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
            <p>Documentation:</p>
            <ul>
                <li><a href="/docs">/docs</a> - FastAPI auto-generated documentation</li>
                <li><a href="/redoc">/redoc</a> - FastAPI auto-generated documentation (redoc)</li>
            </ul>
        </body>
    </html>
    """

#################################
#    CONNECTIONS ENDPOINTS      #
#################################


@app.get("/connections/", description="Get today's connections game", response_description="Daily Connections retrieved")
@limiter.limit("1/second")
async def get_the_daily_connections(request: Request):
    current_date = datetime.now()
    connection = await retrieve_connections_by_date(current_date.strftime('%Y-%m-%d'))
    if not connection:
        return ResponseModel(connection, "Empty list returned")
    return ResponseModel(connection, "Data retrieved successfully")

@app.get("/{date}", description="Get a connections game at a specific date", response_description="Connections retrieved at a specific date")
@limiter.limit("1/second")
async def get_connections_by_date(date, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return ErrorResponseModel("An error occurred.", 404, "Invalid date format or Connections data doesn't exist for that date.")
    return ResponseModel(connection, "Connections data retrieved successfully from " + date)


#############################
#    Words ENDPOINT         #
#############################
@app.get("/{date}/words", description="Get all 16 words of a connections game at a specific date",response_description="Just the words of the connections")
@limiter.limit("2/second")
async def get_words(date: str, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return ErrorResponseModel("An error occurred.", 404, "Invalid date format or Connections data doesn't exist for that date.")
    
    words = []
    print(connection)
    for answer in connection["answers"]:
        words.extend(answer["members"])
    
    return ResponseModel(words, "Words retrieved successfully")

#################################
#    CATEGORIES ENDPOINT        #
#################################

@app.get("/{date}/categories", description="Get all 4 categories of a connections game at a specific date", response_description="Just the categories of the connections")
@limiter.limit("1/second")
async def get_categories(date: str, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return HTTPException(status_code=404, detail="Invalid date format or Connections data doesn't exist for that date.")
    
    categories = []
    for answer in connection["answers"]:
        categories.append(answer["group"])
    
    return ResponseModel(categories, "Categories retrieved successfully")

@app.get("/{date}/categories/complete", description="Get all categories and words of a connections game at a specific date", response_description="The categories and words of the connections")
@limiter.limit("1/second")
async def get_categories_and_words(date: str, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return HTTPException(status_code=404, detail="Invalid date format or Connections data doesn't exist for that date.")
    
    categories_and_words = []
    for answer in connection["answers"]:
        categories_and_words.append({
            "group": answer["group"],
            "members": answer["members"]
        })
    
    return ResponseModel(categories_and_words, "Categories and words retrieved successfully")

@app.get("/{date}/categories/{level}", description="Get the category of a connections game at a specific date and level", response_description="The category of the connections")
@limiter.limit("1/second")
async def get_category(date: str, level: int, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return HTTPException(status_code=404, detail="Invalid date format or Connections data doesn't exist for that date.")
    
    if level < 0 or level > 3:
        return HTTPException(status_code=400, detail="Invalid level")
    
    category = connection["answers"][level]["group"]
    return ResponseModel(category, "Category retrieved successfully")

@app.get("/{date}/categories/{level}/words", description="Get the words that belong to a category at a specific date", response_description="The words of the connections")
@limiter.limit("1/second")
async def get_words_by_category(date: str, level: int, request: Request):
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return HTTPException(status_code=404, detail="Invalid date format or Connections data doesn't exist for that date.")
    
    if level < 0 or level > 3:
        return HTTPException(status_code=400, detail="Invalid level")
    
    words = connection["answers"][level]["members"]
    return ResponseModel(words, "Words retrieved successfully")
    

#################################
#    GUESS ENDPOINT             #
#################################
class GuessRequest(BaseModel):
    guess: list[str]

    @validator('guess')
    def validate_guess_length(cls, v):
        if len(v) != 4:
            raise ValueError('Guess must contain exactly 4 strings')
        return v

@app.post("/{date}/guess", description="Guess a 4-word category of a connections game at a specific date", response_description="The level and group of the guess. -1 if incorrect. 0-3 otherwise.")
@limiter.limit("1/second")
async def guess(date: str, request: Request, body: GuessRequest = Body(...)):
    try:
        validated_guess = body
    except ValidationError as e:
        return ErrorResponseModel("An error occurred.", 400, str(e))
    
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return ErrorResponseModel("An error occurred.", 404, "Invalid date format or Connections data doesn't exist for that date.")
    
    response = {
        "level": -1,
        "group": ""
    }
    message = "Guess is incorrect"

    validated_guess.guess.sort()
    for answer in connection["answers"]:
        answer["members"].sort()
        if answer["members"] == validated_guess.guess:
            response["level"] = answer["level"]
            response["group"] = answer["group"]
            message = "Guess is correct"
            break
    
    return ResponseModel(response, message)
    

#################################
#    HINT ENDPOINT             #
#################################
class HintRequest(BaseModel):
    level: int
    prev_hints: int = 0

    @validator('level')
    def validate_level(cls, v):
        if v < 0 or v > 3:
            raise ValueError('Level must be between 0 and 3')
        return v

@app.post("/{date}/hint", description="Get a hint for a connections game at a specific date", response_description="A hint for the connections game")
@limiter.limit("1/second")
async def hint(date: str, request: Request, body: HintRequest = Body(...)):
    try:
        validated_hint = body
    except ValidationError as e:
        return ErrorResponseModel("An error occurred.", 400, str(e))
    
    connection = await retrieve_connections_by_date(date)
    if not connection:
        return HTTPException(status_code=404, detail="Invalid date format or Connections data doesn't exist for that date.")
    
    prev_hints = int(validated_hint.prev_hints)
    group = connection["answers"][validated_hint.level]["group"]
    correct_group = connection["answers"][validated_hint.level]["members"]

    if not correct_group or group == "":
        return HTTPException(status_code=400, detail="Invalid level")

    if prev_hints > 3:
        raise HTTPException(status_code=400, detail="Too many hints requested for this level")
    
    if prev_hints == 3:
        return ResponseModel(f"The words in the group are {', '.join(correct_group)}", "Hint generated successfully")

    if prev_hints == 2:
        return ResponseModel(f"The grouping for level {validated_hint.level+1} is {group}", "Hint generated successfully")

    if prev_hints == 1:
        return ResponseModel(f"Two of the words in level {validated_hint.level+1} are {correct_group[0]} and {correct_group[1]}", "Hint generated successfully")

    sys_prompt = f"These four words ({', '.join(correct_group)}) are connected by the common theme: {group}. Give an extremely short hint or riddle. Trim all extra words, but DO NOT GIVE AWAY THE ANSWER OR USE THE WORDS IN THE GROUP."
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": "One hint please!"}
            ]
        )
        return ResponseModel(completion.choices[0].message.content, "Hint generated successfully")
    except Exception as e:
        return HTTPException(status_code=500, detail="Error generating hint")
    

    