from pydantic import BaseModel, Field, ConfigDict

class LevelBase(BaseModel):
    """Base schema for level data"""
    code: str = Field(..., min_length=1)
    description: str
    level: int = Field(..., ge=1)

class LevelCreate(LevelBase):
    """Schema for level creation"""
    pass

class LevelRead(LevelBase):
    """Schema for reading level data"""
    id: int
    
    model_config = ConfigDict(from_attributes=True) 