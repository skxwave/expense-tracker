class DomainException(Exception):
    """Base class for all business logic exceptions."""

    def __init__(self, message: str):
        self.message = message


class EntityNotFoundError(DomainException):
    """Raised when a requested entity does not exist."""

    pass


class EntityAlreadyExistsError(DomainException):
    """Raised when trying to create an entity that already exists."""

    pass


class InvalidCredentialsError(DomainException):
    """Raised during failed login attempts."""

    pass
