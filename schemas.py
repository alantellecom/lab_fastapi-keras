
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    role: str
    password: str

class ShowUser(BaseModel):
     name: str
     email: str
     role: str
     class Config():
        orm_mode = True
