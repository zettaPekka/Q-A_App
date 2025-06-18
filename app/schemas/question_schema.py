from pydantic import BaseModel


class QuestionSchema(BaseModel):
    title: str
    content: str