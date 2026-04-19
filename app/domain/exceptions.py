class DomainException(Exception):
    pass


class UserNotFound(DomainException):
    def __init__(self, identifier: str = ""):
        super().__init__(f"User not found: {identifier}" if identifier else "User not found")


class UserAlreadyExists(DomainException):
    def __init__(self, email: str = ""):
        super().__init__(f"User already exists with email: {email}" if email else "User already exists")


class ServiceNotFound(DomainException):
    def __init__(self, identifier: str = ""):
        super().__init__(f"Service not found: {identifier}" if identifier else "Service not found")


class BookingNotFound(DomainException):
    def __init__(self, identifier: str = ""):
        super().__init__(f"Booking not found: {identifier}" if identifier else "Booking not found")


class BookingConflict(DomainException):
    def __init__(self) -> None:
        super().__init__("A booking already exists for this service at the requested time")


class InvalidBookingTransition(DomainException):
    def __init__(self, from_status: str, to_status: str) -> None:
        super().__init__(f"Cannot transition booking from '{from_status}' to '{to_status}'")


class PermissionDenied(DomainException):
    def __init__(self, reason: str = "") -> None:
        super().__init__(f"Permission denied: {reason}" if reason else "Permission denied")


class InvalidEmailFormat(DomainException):
    def __init__(self, email: str = "") -> None:
        super().__init__(f"Invalid email format: {email}" if email else "Invalid email format")


class InvalidCredentials(DomainException):
    def __init__(self) -> None:
        super().__init__("Invalid credentials")
