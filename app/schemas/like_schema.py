from pydantic import BaseModel


class LikeSchema(BaseModel):
    answer_id: int
    user_id: int
