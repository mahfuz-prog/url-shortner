from fastapi import HTTPException


class ServerError(HTTPException):
    """Base exception for server errors"""

    pass


class InternalServerError(ServerError):
    def __init__(self):
        super().__init__(status_code=500, detail="An unexpected error occurred")


class UserError(HTTPException):
    """Base exception for user-related errors"""

    pass


class UserEmailConflictError(UserError):
    def __init__(self):
        super().__init__(status_code=409, detail="Email already registered")


class UserUserNameConflictError(UserError):
    def __init__(self):
        super().__init__(status_code=409, detail="Username already registered")


class AuthenticationError(UserError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(status_code=401, detail=message)


class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = (
            "User not found" if user_id is None else f"User with id {user_id} not found"
        )
        super().__init__(status_code=404, detail=message)


class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")


class UrlError(HTTPException):
    """Base exception for url-related errors"""

    pass


class UrlNotFoundError(UrlError):
    def __init__(self, short_code: str):
        message = f"{short_code} corresponding long url not found"
        super().__init__(status_code=404, detail=message)
