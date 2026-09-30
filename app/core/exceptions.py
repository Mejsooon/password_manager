class AppException(Exception):
    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        message = detail or self.detail
        super().__init__(message)
        self.detail = message


class UsernameAlreadyExistsError(AppException):
    status_code = 409
    detail = "Nazwa użytkownika jest już zajęta."


class InvalidCredentialsError(AppException):
    status_code = 401
    detail = "Incorrect username or password"


class PasswordNotFoundError(AppException):
    status_code = 404
    detail = "Hasło nie istnieje."


class SessionInvalidError(AppException):
    status_code = 401
    detail = "Session expired"