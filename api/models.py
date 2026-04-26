from pydantic import BaseModel, Field

class ProcessRequest(BaseModel):
    url: str = Field(..., description="The Instagram Reel URL to process")

class ProcessResponse(BaseModel):
    reel_id: str
    message: str
    transcript: str
    visual_description: str

class QueryRequest(BaseModel):
    reel_id: str = Field(..., description="The ID of the processed reel")
    question: str = Field(..., description="The question to ask about the reel")

class QueryResponse(BaseModel):
    answer: str
