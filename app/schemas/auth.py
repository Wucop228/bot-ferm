from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    login: EmailStr
    password: str