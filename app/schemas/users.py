from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
  phone_number: Optional[str] = None
  postal_address: Optional[str] = None
  email: EmailStr

class UserCreate(UserBase):
  password: str

class UserOut(BaseModel):
  id: int
  full_name: str
  email: str
  phone_number: Optional[str] = None
  postal_address: Optional[str] = None
  status: Optional[str] = "active"
  type: str
  model_config = ConfigDict(from_attributes=True)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str
    confirm_password: str