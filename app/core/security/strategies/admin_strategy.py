from app.core.security.permissions import PermissionStrategy


class AdminPermissionStrategy(PermissionStrategy):
    def can_access_admin_panel(self) -> bool:
        return True

    def can_manage_services(self) -> bool:
        return True

    def can_create_booking(self) -> bool:
        return True

    def can_manage_all_users(self) -> bool:
        return True

    def can_view_all_bookings(self) -> bool:
        return True
