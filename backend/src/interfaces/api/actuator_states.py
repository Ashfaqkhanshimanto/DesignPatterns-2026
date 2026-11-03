
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.actuators.service import (
    ActuatorNotFoundError,
    ActuatorStateService,
)
from domain.actuators.state import IllegalTransitionError
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/devices",
    tags=["actuator states"],
)


class ActuatorStateDto(BaseModel):
    device_id: UUID
    state: str
    allowed_commands: list[str]


class TransitionRequest(BaseModel):
    target: str


def get_actuator_service(
    db: Session = Depends(get_db),
) -> ActuatorStateService:
    repository = ActuatorStateRepository(db)
    return ActuatorStateService(repository)


@router.get(
    "/{device_id}/state",
    response_model=ActuatorStateDto,
)
def get_actuator_state(
    device_id: UUID,
    service: ActuatorStateService = Depends(
        get_actuator_service
    ),
) -> ActuatorStateDto:
    try:
        context = service.get_state(device_id)

    except ActuatorNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return ActuatorStateDto(
        device_id=context.device_id,
        state=context.state,
        allowed_commands=context.allowed_commands,
    )


@router.post(
    "/{device_id}/transition",
    response_model=ActuatorStateDto,
)
def transition_actuator(
    device_id: UUID,
    request: TransitionRequest,
    service: ActuatorStateService = Depends(
        get_actuator_service
    ),
) -> ActuatorStateDto:
    try:
        context = service.transition(
            device_id,
            request.target,
        )

    except ActuatorNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IllegalTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return ActuatorStateDto(
        device_id=context.device_id,
        state=context.state,
        allowed_commands=context.allowed_commands,
    )
