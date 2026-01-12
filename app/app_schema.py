from pydantic import BaseModel

class RequestBody(BaseModel):
    question: str
    file_id: str

class SectionIDBody(BaseModel):
    file_id: str