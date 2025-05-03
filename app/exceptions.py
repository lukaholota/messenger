from fastapi import HTTPException, status


class ServiceException(Exception):
    pass


class DatabaseError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail or f"A database error occurred"
        super().__init__(self.detail)


class DuplicateEmailException(ServiceException):
    def __init__(self, email: str, detail: str | None = None):
        self.email = email
        self.detail = detail or f"Email '{email}' already exists"
        super().__init__(self.detail)


class DuplicateUsernameException(ServiceException):
    def __init__(self, username: str, detail: str | None = None):
        self.username = username
        self.detail = detail or f"Username '{username}' already exists"
        super().__init__(self.detail)


class InvalidCredentialsException(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail or 'Username or password is incorrect'
        super().__init__(self.detail)


class ChatValidationError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.detail)


class UsersNotFoundError(ServiceException):
    def __init__(self, detail: str | None = None, missing_ids: set = None):
        self.detail = detail
        self.missing_ids = missing_ids
        super().__init__(self.detail)


class InvalidAccessTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token',
            headers={"WWW-Authenticate": "Bearer"}
        )
