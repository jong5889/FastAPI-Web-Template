from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class GoogleIdToken(BaseModel):
    id_token_str: str

class MFAEnable(BaseModel):
    code: str

class MFACode(BaseModel):
    code: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    mfa_enabled: bool

    class Config:
        orm_mode = True
