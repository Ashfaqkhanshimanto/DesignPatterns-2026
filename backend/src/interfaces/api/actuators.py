
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from application.actuators.execution_service import (
    ActuatorExecutionService,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeExceededError,
)
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/actuators",
    tags=["actuator executions"],
)


class ExecutionDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    success: bool
    policy_applied: list[str]
    message: str | None
    created_at: datetime


class ApplyRequest(BaseModel):
    device_id: UUID
    command: str
    payload: dict[str, object] = Field(default_factory=dict)


@router.get(
    "/executions",
    response_model=list[ExecutionDto],
    summary="List recent actuator executions",
)
def list_executions(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ExecutionDto]:
    service = ActuatorExecutionService(db)

    rows = service.list_recent(limit)

    return [
        ExecutionDto.model_validate(row)
        for row in rows
    ]


@router.post(
    "/apply",
    summary="Apply a simulated actuator command",
)
def apply_actuator_command(
    request: ApplyRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # Confirm the device exists and is an actuator.
    state_repository = ActuatorStateRepository(db)

    actuator = state_repository.get_actuator(
        request.device_id
    )

    if actuator is None:
        raise HTTPException(
            status_code=404,
            detail="Actuator not found",
        )

    service = ActuatorExecutionService(db)

    try:
        service.apply(
            device_id=request.device_id,
            command=request.command,
            payload=request.payload,
        )

    except MaxRuntimeExceededError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {
        "status": "success",
        "message": "Simulated actuator command applied",
    }
