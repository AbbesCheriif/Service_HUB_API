import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.infrastructure.database.models.base import Base


class ServiceModel(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    provider: Mapped["UserModel"] = relationship("UserModel", back_populates="services")  # noqa: F821
    bookings: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="service", lazy="selectin")  # noqa: F821
    reviews: Mapped[list["ReviewModel"]] = relationship("ReviewModel", back_populates="service", lazy="selectin")  # noqa: F821
