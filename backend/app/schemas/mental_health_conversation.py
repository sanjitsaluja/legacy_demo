from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MentalHealthConversationBase(BaseModel):
    question: str
    answer: str


class MentalHealthConversationCreate(MentalHealthConversationBase):
    pass


class MentalHealthConversation(MentalHealthConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
