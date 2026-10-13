
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from application.automation.dto import (
    AutomationEvaluationDto,
    StrategyRead,
    StrategySaveRequest,
)
from application.automation.service import (
    AutomationLocationNotFoundError,
    AutomationService,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/locations",
    tags=["automation"],
)


def get_automation_service(
    db: Session = Depends(get_db),
) -> AutomationService:
    repository = AutomationRepository(db)
    return AutomationService(repository)


@router.put(
    "/{location_id}/automation/strategy",
    response_model=StrategyRead,
)
def save_strategy(
    location_id: UUID,
    request: StrategySaveRequest,
    service: AutomationService = Depends(
        get_automation_service
    ),
) -> StrategyRead:
    try:
        return service.save_strategy(
            location_id,
            request.strategy_key,
        )

    except AutomationLocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/{location_id}/automation/strategy",
    response_model=StrategyRead,
)
def get_saved_strategy(
    location_id: UUID,
    service: AutomationService = Depends(
        get_automation_service
    ),
) -> StrategyRead:
    try:
        return service.get_saved_strategy(location_id)

    except AutomationLocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/{location_id}/automation/evaluate",
    response_model=AutomationEvaluationDto,
)
def evaluate_automation(
    location_id: UUID,
    service: AutomationService = Depends(
        get_automation_service
    ),
) -> AutomationEvaluationDto:
    try:
        return service.evaluate(location_id)

    except AutomationLocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
