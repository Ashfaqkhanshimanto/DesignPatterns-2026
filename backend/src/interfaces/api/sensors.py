from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.readings.dto import ReadingDto
from application.readings.service import (
    AdapterSelectionError,
    DeviceNotFoundError,
    ReadingIngest,
)
from application.sensors.service import SensorService
from domain.sensors.entity import Sensor
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class SensorCreateRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    id: UUID
    device_type: str
    display_name: str
    default_config: dict[str, object]


def to_response(sensor: Sensor) -> SensorResponse:
    if sensor.id is None:
        raise RuntimeError("Persisted sensor has no id")

    return SensorResponse(
        id=sensor.id,
        device_type=sensor.device_type,
        display_name=sensor.display_name,
        default_config=sensor.default_config,
    )


@router.get(
    "",
    response_model=list[SensorResponse],
)
def list_sensors(
    db: Session = Depends(get_db),
) -> list[SensorResponse]:
    service = SensorService(DeviceRepository(db))

    return [
        to_response(sensor)
        for sensor in service.list_sensors()
    ]


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    db: Session = Depends(get_db),
) -> SensorResponse:
    service = SensorService(DeviceRepository(db))

    try:
        sensor = service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return to_response(sensor)


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def read_sensor(
    device_id: UUID,
    db: Session = Depends(get_db),
) -> ReadingDto:
    device_repository = DeviceRepository(db)
    reading_repository = ReadingRepository(db)

    service = ReadingIngest(
        device_repository,
        reading_repository,
    )

    try:
        return service.record(device_id)

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AdapterSelectionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def list_sensor_readings(
    device_id: UUID,
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
) -> list[ReadingDto]:
    device_repository = DeviceRepository(db)

    device = device_repository.get_device(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} was not found.",
        )

    if device.role != "sensor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device {device_id} is not a sensor.",
        )

    reading_repository = ReadingRepository(db)

    readings = reading_repository.list_recent(
        device_id=device_id,
        limit=limit,
    )

    return [
        ReadingDto(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )
        for reading in readings
    ]