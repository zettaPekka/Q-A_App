from pydantic import BaseModel, Field


class QuestionSchema(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(min_length=10, max_length=5000)
    anonymous: bool = False
    tags: list[str] = Field(default=[]) #  TODO: add tags validation
