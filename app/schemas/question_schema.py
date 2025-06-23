from pydantic import BaseModel, Field
from typing import List


class QuestionSchema(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(min_length=10, max_length=5000)
    anonymous: bool = False
    tags: List[str] = Field(default=[], max_length=5)
