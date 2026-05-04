from pydantic import BaseModel, EmailStr, model_validator
class UpdatePasswordRequest(BaseModel):
  current_password: str
  new_password: str
  confirm_new_password: str
  @model_validator(mode='after')
  def validate_passwords(self):
    if self.new_password != self.confirm_new_password:
      raise ValueError('New password and confirm new password do not match')
    return self