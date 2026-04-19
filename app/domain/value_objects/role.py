from enum import Enum


class Role(str, Enum):
    CLIENT = "CLIENT"
    PROVIDER = "PROVIDER"
    ADMIN = "ADMIN"
