from uuid import UUID

from app.application.dto.booking_dto import BookingCreateDTO, BookingReadDTO
from app.application.dto.service_dto import ServiceCreateDTO, ServiceReadDTO
from app.application.dto.user_dto import UserCreateDTO, UserReadDTO
from app.domain.entities.booking import Booking
from app.domain.entities.service import Service
from app.domain.entities.user import User
from app.domain.value_objects.email import Email


def user_to_dto(user: User) -> UserReadDTO:
    return UserReadDTO(
        id=user.id,
        email=str(user.email),
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        bio=user.bio,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def dto_to_user(dto: UserCreateDTO, hashed_password: str) -> User:
    return User(
        email=Email(dto.email),
        full_name=dto.full_name,
        hashed_password=hashed_password,
        role=dto.role,
    )


def service_to_dto(service: Service) -> ServiceReadDTO:
    return ServiceReadDTO(
        id=service.id,
        provider_id=service.provider_id,
        title=service.title,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        is_active=service.is_active,
        category=service.category,
        average_rating=service.average_rating,
        total_reviews=service.total_reviews,
        created_at=service.created_at,
        updated_at=service.updated_at,
    )


def dto_to_service(dto: ServiceCreateDTO, provider_id: UUID) -> Service:
    return Service(
        provider_id=provider_id,
        title=dto.title,
        description=dto.description,
        price=dto.price,
        duration_minutes=dto.duration_minutes,
        category=dto.category,
    )


def booking_to_dto(booking: Booking) -> BookingReadDTO:
    return BookingReadDTO(
        id=booking.id,
        client_id=booking.client_id,
        service_id=booking.service_id,
        provider_id=booking.provider_id,
        scheduled_at=booking.scheduled_at,
        status=booking.status,
        notes=booking.notes,
        total_price=booking.total_price,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


def dto_to_booking(
    dto: BookingCreateDTO,
    client_id: UUID,
    provider_id: UUID,
    total_price: float,
) -> Booking:
    return Booking(
        client_id=client_id,
        service_id=dto.service_id,
        provider_id=provider_id,
        scheduled_at=dto.scheduled_at,
        notes=dto.notes,
        total_price=total_price,
    )
