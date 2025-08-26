from pydantic import BaseModel


class ContactCreate(BaseModel):
    contact_id: int
    name: str

class ContactUpdate(BaseModel):
    contact_id: int
    name: str | None = None

class ContactRead(BaseModel):
    contact_id: int
    name: str

    class Config:
        from_attributes = True
