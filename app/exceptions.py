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


class UserNotFoundError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.detail)


class MessageValidationError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.detail)


class DeletedUserServiceError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.detail)


class UserDeleteError(ServiceException):
    def __init__(self, detail: str | None = None):
        self.detail = detail
        super().__init__(self.detail)


class DeletedUserError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='This user is deleted',
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidAccessTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token',
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidTokenCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )


class RedisConnectionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='redis connection error',
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenInvalidatedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Token invalidated error',
            headers={"WWW-Authenticate": "Bearer"}
        )


class MessagingError(Exception):
    pass


class MessagingConnectionError(MessagingError):
    pass


class MessagePublishError(MessagingError):
    pass


class InvalidMessageDataError(ValueError):
    pass
