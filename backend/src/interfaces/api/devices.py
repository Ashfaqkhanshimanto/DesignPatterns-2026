
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from application.actuators.service import ActuatorStateService
from application.commands.service import commands_allowed_for_device
from application.devices.assignment_service import (
    DeviceAssignmentService,
    DeviceNotFoundError,
    ZoneNotFoundError,
)
from application.devices.dto import (
    DeviceDto,
    DeviceSamplingRequest,
    DeviceZoneAssignmentRequest,
)
from application.devices.family_service import DeviceFamilyService
from application.devices.mappers import device_to_dto, devices_to_dtos
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


# ---------------------------------------------------------
# Phase 8 and Phase 10 - Actuator state information
# ---------------------------------------------------------

def add_actuator_state(
    device: DeviceDto,
    state_service: ActuatorStateService,
) -> DeviceDto:
    # Sensors do not have actuator lifecycle states.
    if device.role != "actuator":
        return device

    # Read the actuator's real saved state.
    context = state_service.get_state(device.id)

    device.state = context.state

    # Include Phase 10 device-specific allowed commands.
    # A running grow light can use set_light_level.
    device.allowed_commands = commands_allowed_for_device(
        context,
        device.device_type,
    )

    return device


def add_actuator_states(
    devices: list[DeviceDto],
    db: Session,
) -> list[DeviceDto]:
    state_service = ActuatorStateService(
        ActuatorStateRepository(db)
    )

    return [
        add_actuator_state(device, state_service)
        for device in devices
    ]


# ---------------------------------------------------------
# Phase 3 - List devices
# ---------------------------------------------------------

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

    result = devices_to_dtos(devices)

    return add_actuator_states(result, db)


# ---------------------------------------------------------
# Phase 3 - Provision device families
# ---------------------------------------------------------

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

    result = devices_to_dtos(devices)

    # Initialize actuator states where necessary.
    return add_actuator_states(result, db)


# ---------------------------------------------------------
# Phase 4 - Assign or unassign devices to zones
# ---------------------------------------------------------

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

    result = device_to_dto(device)

    return add_actuator_states([result], db)[0]


# ---------------------------------------------------------
# Phase 5 - Update sampling settings
# ---------------------------------------------------------

@router.patch(
    "/{device_id}/sampling",
    response_model=DeviceDto,
)
def update_device_sampling(
    device_id: UUID,
    request: DeviceSamplingRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    repository = DeviceRepository(db)

    device = repository.update_sampling(
        device_id=device_id,
        sampling_interval_seconds=request.sampling_interval_seconds,
        tracking_enabled=request.tracking_enabled,
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} was not found.",
        )

    result = device_to_dto(device)

    return add_actuator_states([result], db)[0]
