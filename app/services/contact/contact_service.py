from app.db.repository.contact_repository import ContactRepository
from app.db.repository.user_repository import UserRepository
from app.schemas.contact import ContactCreate, ContactRead


class ContactService:
    def __init__(
            self,
            contact_repository: ContactRepository,
            user_repository: UserRepository
    ):
        self.contact_repository = contact_repository
        self.user_repository = user_repository

    async def add_to_contacts(
            self, contact_create: ContactCreate, user_id: int
    ) -> ContactRead:
        contact = self.contact_repository.create_contact(
            contact_id=contact_create.contact_id,
            user_id=user_id,
            name=contact_create.name
        )
        return ContactRead.model_validate(contact)

    async def get_contacts(self, user_id: int):
        contacts = await self.contact_repository.get_contacts(user_id)

        return [
            ContactRead.model_validate(contact) for contact in contacts
        ]