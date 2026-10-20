from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.auth.auth_model import Role

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=12)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    email: EmailStr
    role: Role


class UserLogin(BaseModel):
    email: EmailStr
    password : str


class TokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RefreshRequest(BaseModel):
    refresh_token: str
    
