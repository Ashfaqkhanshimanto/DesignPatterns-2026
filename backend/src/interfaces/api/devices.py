from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from application.devices.assignment_service import (
    DeviceAssignmentService,
    DeviceNotFoundError,
    ZoneNotFoundError,
)
from application.devices.dto import (
    DeviceDto,
    DeviceZoneAssignmentRequest,
)
from application.devices.family_service import DeviceFamilyService
from application.devices.mappers import device_to_dto, devices_to_dtos
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


@router.get(
    "",
    response_model=list[DeviceDto],
)
def list_devices(
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    service = DeviceFamilyService(
        DeviceRepository(db)
    )

    devices = service.list_devices(
        family=family,
        role=role,
    )

    return devices_to_dtos(devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    service = DeviceFamilyService(
        DeviceRepository(db)
    )

    try:
        devices = service.provision_family(family)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return devices_to_dtos(devices)


@router.patch(
    "/{device_id}/zone",
    response_model=DeviceDto,
)
def assign_device_to_zone(
    device_id: UUID,
    request: DeviceZoneAssignmentRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    service = DeviceAssignmentService(
        DeviceRepository(db)
    )

    try:
        if request.zone_id is None:
            device = service.unassign_device(
                device_id=device_id,
            )
        else:
            device = service.assign_device(
                device_id=device_id,
                zone_id=request.zone_id,
            )

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ZoneNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return device_to_dto(device)