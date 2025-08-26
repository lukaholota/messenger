from app.db.repository.user_repository import UserRepository
from app.schemas.search import SearchIn, SearchOut
from app.schemas.user import SearchUser


class SearchService:
    def __init__(
            self,
            user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def search(self, data_in: SearchIn, user_id: int):
        if len(data_in.prompt) <= 3:
            return SearchOut(found_users=[])

        found_users_raw = await self.user_repository.search_users_raw(
            prompt=data_in.prompt, user_id=user_id
        )


        return SearchOut(
            found_users = [
                SearchUser(
                    user_id=found_user_id,
                    username=username,
                    display_name=contact_name or display_name,
                    is_contact=bool(contact_name)
                ) for found_user_id, username, display_name,
                                contact_name in found_users_raw
            ]
        )
