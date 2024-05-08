from pydantic import BaseModel, Field

class Category(BaseModel):
    """
    Model for a single category containing words.
    """
    group: str = Field(...)
    level: int = Field(...)
    members: list = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "level": 0,
                "group": "category1",
                "members": ["word1", "word2", "word3", "word4"]
            }
        }

class Connections(BaseModel):
    """
    Container for a single connections record.
    """

    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: int = Field(alias="_id", default=None)
    NYT_id: int = Field(...)
    date: str = Field(...)
    author: str = Field(...)
    categories: list = [Category]
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "_id": 1,
                "NYT_id": 1,
                "date": "2021-01-01",
                "author": "Author Name",
                "answers": [
                    {
                        "level": 0,
                        "group": "category1",
                        "members": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "level": 1,
                        "group": "category2",
                        "members": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "level": 2,
                        "group": "category3",
                        "members": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "level": 2,
                        "group": "category4",
                        "members": ["word1", "word2", "word3", "word4"]
                    }
                ]
            }
        }

def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}