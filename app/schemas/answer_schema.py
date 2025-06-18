from pydantic import BaseModel


class AnswerSchema(BaseModel):
    content: str
