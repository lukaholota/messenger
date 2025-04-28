from app.db.repository.user_repository import user_repository, UserRepository


def get_user_repository() -> UserRepository:
    return user_repository