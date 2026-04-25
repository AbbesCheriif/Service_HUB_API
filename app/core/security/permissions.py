from abc import ABC, abstractmethod


class PermissionStrategy(ABC):
    @abstractmethod
    def can_access_admin_panel(self) -> bool: ...

    @abstractmethod
    def can_manage_services(self) -> bool: ...

    @abstractmethod
    def can_create_booking(self) -> bool: ...

    @abstractmethod
    def can_manage_all_users(self) -> bool: ...

    @abstractmethod
    def can_view_all_bookings(self) -> bool: ...
