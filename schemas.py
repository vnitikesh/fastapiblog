from pydantic import BaseModel, EmailStr
from typing import List, Optional

class PostSchema(BaseModel):
    title: str
    content: str

class Blog(BaseModel):
    title: str
    body: str

class ShowBlog(BaseModel):
    title: str
    body: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Nitikesh",
                "last_name": "Vishal",
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }


class BookBase(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

class AuthorBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class AssistantBase(BaseModel):
    id: int
    name: str

class BookSchema(BookBase):
    authors: List[AuthorBase]
    assistant: Optional[List[AssistantBase]]

class AuthorSchema(AuthorBase):
    books: List[BookBase]
    asssistant: List[AssistantBase]