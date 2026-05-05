import pytest

from app.core.security.strategies.admin_strategy import AdminPermissionStrategy
from app.core.security.strategies.client_strategy import ClientPermissionStrategy
from app.core.security.strategies.provider_strategy import ProviderPermissionStrategy


class TestAdminPermissionStrategy:
    def setup_method(self):
        self.strategy = AdminPermissionStrategy()

    def test_can_access_admin_panel(self):
        assert self.strategy.can_access_admin_panel() is True

    def test_can_manage_services(self):
        assert self.strategy.can_manage_services() is True

    def test_can_create_booking(self):
        assert self.strategy.can_create_booking() is True

    def test_can_manage_all_users(self):
        assert self.strategy.can_manage_all_users() is True

    def test_can_view_all_bookings(self):
        assert self.strategy.can_view_all_bookings() is True


class TestProviderPermissionStrategy:
    def setup_method(self):
        self.strategy = ProviderPermissionStrategy()

    def test_cannot_access_admin_panel(self):
        assert self.strategy.can_access_admin_panel() is False

    def test_can_manage_services(self):
        assert self.strategy.can_manage_services() is True

    def test_cannot_create_booking(self):
        assert self.strategy.can_create_booking() is False

    def test_cannot_manage_all_users(self):
        assert self.strategy.can_manage_all_users() is False

    def test_cannot_view_all_bookings(self):
        assert self.strategy.can_view_all_bookings() is False


class TestClientPermissionStrategy:
    def setup_method(self):
        self.strategy = ClientPermissionStrategy()

    def test_cannot_access_admin_panel(self):
        assert self.strategy.can_access_admin_panel() is False

    def test_cannot_manage_services(self):
        assert self.strategy.can_manage_services() is False

    def test_can_create_booking(self):
        assert self.strategy.can_create_booking() is True

    def test_cannot_manage_all_users(self):
        assert self.strategy.can_manage_all_users() is False

    def test_cannot_view_all_bookings(self):
        assert self.strategy.can_view_all_bookings() is False


def test_strategies_are_distinct():
    admin = AdminPermissionStrategy()
    provider = ProviderPermissionStrategy()
    client = ClientPermissionStrategy()

    assert admin.can_access_admin_panel() != provider.can_access_admin_panel()
    assert admin.can_access_admin_panel() != client.can_access_admin_panel()
    assert provider.can_manage_services() == admin.can_manage_services()
    assert client.can_manage_services() != provider.can_manage_services()
    assert client.can_create_booking() == admin.can_create_booking()
    assert provider.can_create_booking() != client.can_create_booking()
