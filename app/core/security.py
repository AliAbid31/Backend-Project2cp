import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta,timezone
def create_access_token(data:dict):
  to_encode=data.copy()
  expire=datetime.now(timezone.utc)+timedelta(days=36500)
  to_encode.update({"exp":expire})
  encoded_jwt=jwt.encode(to_encode, "HelloWorld123", algorithm="HS256")
  return encoded_jwt

def hash_password(password: str):
  password_bytes = password.encode("utf-8")
  return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(given_password: str, hashed_password: str):
  try:
    return bcrypt.checkpw(given_password.encode("utf-8"), hashed_password.encode("utf-8"))
  except Exception:
    return False


def password_matches(given_password: str, stored_password: str):
  return stored_password == given_password or verify_password(given_password, stored_password)





