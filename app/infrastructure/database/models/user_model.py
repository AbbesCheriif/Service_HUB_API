import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.value_objects.role import Role
from app.infrastructure.database.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum(Role), nullable=False, default=Role.CLIENT)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    services: Mapped[list["ServiceModel"]] = relationship("ServiceModel", back_populates="provider", lazy="selectin")  # noqa: F821
    bookings: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="client", lazy="selectin", foreign_keys="BookingModel.client_id")  # noqa: F821
    file_uploads: Mapped[list["FileUploadModel"]] = relationship("FileUploadModel", back_populates="uploader", lazy="selectin")  # noqa: F821
