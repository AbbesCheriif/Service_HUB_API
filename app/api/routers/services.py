from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, require_role
from app.api.dependencies.database import get_session
from app.api.schemas.service_schema import ServiceCreateRequest, ServiceResponse, ServiceUpdateRequest
from app.application.dto.service_dto import ServiceCreateDTO
from app.application.use_cases.service.create_service import CreateService
from app.application.use_cases.service.list_services import ListServices
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ServiceNotFound
from app.domain.value_objects.role import Role
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    payload: ServiceCreateRequest,
    current_user: Annotated[User, Depends(require_role(Role.PROVIDER, Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = CreateService(uow=uow)
    dto = ServiceCreateDTO(**payload.model_dump())
    return await use_case.execute(dto, provider_id=current_user.id)


@router.get("/", response_model=list[ServiceResponse])
async def list_services(
    offset: int = 0,
    limit: int = 20,
    session: Annotated[AsyncSession, Depends(get_session)] = ...,
):
    uow = SQLAlchemyUnitOfWork(session)
    use_case = ListServices(uow=uow)
    return await use_case.execute(offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        service = await uow.services.get_by_id(service_id)
    if not service:
        raise ServiceNotFound(str(service_id))
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    payload: ServiceUpdateRequest,
    current_user: Annotated[User, Depends(require_role(Role.PROVIDER, Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        service = await uow.services.get_by_id(service_id)
        if not service:
            raise ServiceNotFound(str(service_id))
        if current_user.role != Role.ADMIN and service.provider_id != current_user.id:
            raise PermissionDenied("only the owner can update this service")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(service, key, value)
        saved = await uow.services.save(service)
        await uow.commit()
    return saved


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: UUID,
    current_user: Annotated[User, Depends(require_role(Role.PROVIDER, Role.ADMIN))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    uow = SQLAlchemyUnitOfWork(session)
    async with uow:
        service = await uow.services.get_by_id(service_id)
        if not service:
            raise ServiceNotFound(str(service_id))
        if current_user.role != Role.ADMIN and service.provider_id != current_user.id:
            raise PermissionDenied("only the owner can delete this service")
        await uow.services.delete(service_id)
        await uow.commit()
