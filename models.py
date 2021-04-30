from sqlalchemy import  Column, Integer, String, Text, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False) 
    email = Column(String, unique=True, nullable=False) 
    password = Column(String, nullable=False)
    role = Column(String)

class Prediction():
    def __init__(self,class_id,class_name):
        self.class_id = class_id
        self.class_name = class_name
