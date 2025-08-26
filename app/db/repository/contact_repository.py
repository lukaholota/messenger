from sqlalchemy import select

from app.db.repository.base import BaseRepository
from app.models import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactRepository(BaseRepository[Contact, ContactCreate, ContactUpdate]):
    async def create_contact(
            self,
            user_id: int,
            contact_id: int,
            name: str
    ) -> Contact:
        contact = Contact(contact_id=contact_id, user_id=user_id, name=name)

        self.db.add(contact)

        return contact

    async def get_contacts(self, user_id: int):
        query = select(Contact).where(Contact.user_id==user_id)
        result = await self.db.execute(query)

        return result.scalars().all()
