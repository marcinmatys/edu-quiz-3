from pydantic import BaseModel

class Token(BaseModel):
    """Schema for token authentication response"""
    access_token: str
    token_type: str 