from fastapi import HTTPException, status


class DuplicateEmailException(HTTPException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' already exists"
        )


class DuplicateUsernameException(HTTPException):
    def __init__(self, username: str):
        self.username = username
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username}' already exists"
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Username or password is incorrect'
        )


class InvalidAccessTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token'
        )
