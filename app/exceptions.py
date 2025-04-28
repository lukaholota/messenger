class DuplicateEmailException(ValueError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email {email} already exists")


class DuplicateUsernameException(ValueError):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Username {username} already exists")
