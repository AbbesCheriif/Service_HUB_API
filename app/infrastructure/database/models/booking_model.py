import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.value_objects.booking_status import BookingStatus
from app.infrastructure.database.models.base import Base


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    client: Mapped["UserModel"] = relationship("UserModel", back_populates="bookings", foreign_keys=[client_id])  # noqa: F821
    service: Mapped["ServiceModel"] = relationship("ServiceModel", back_populates="bookings")  # noqa: F821
    review: Mapped["ReviewModel | None"] = relationship("ReviewModel", back_populates="booking", uselist=False, lazy="selectin")  # noqa: F821
