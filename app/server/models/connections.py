from pydantic import BaseModel, Field

class Category(BaseModel):
    """
    Model for a single category containing words.
    """
    name: str = Field(...)
    words: list = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "name": "category1",
                "words": ["word1", "word2", "word3", "word4"]
            }
        }

class Connections(BaseModel):
    """
    Container for a single connections record.
    """

    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: str = Field(alias="_id", default=None)
    author: str = Field(...)
    categories: list = [Category]
    class Config:
        populate_by_name = True
        schema_extra = {
            "example": {
                "_id": "YYYY-MM-DD",
                "author": "Author Name",
                "categories": [
                    {
                        "category": "category1",
                        "words": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "category": "category2",
                        "words": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "category": "category3",
                        "words": ["word1", "word2", "word3", "word4"]
                    },
                    {
                        "category": "category4",
                        "words": ["word1", "word2", "word3", "word4"]
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