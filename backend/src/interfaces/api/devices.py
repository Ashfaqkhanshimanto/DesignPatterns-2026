from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from application.devices.dto import DeviceDto
from application.devices.family_service import DeviceFamilyService
from application.devices.mappers import devices_to_dtos
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