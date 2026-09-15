from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.sensors.service import SensorService
from domain.sensors.entity import Sensor
from infrastructure.persistence.device_repository import DeviceRepository
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