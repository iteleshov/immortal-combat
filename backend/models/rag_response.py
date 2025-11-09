from pydantic import BaseModel

class RagResponse(BaseModel):
    answer: str