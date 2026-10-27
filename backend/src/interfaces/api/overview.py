
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from application.overview.dto import LocationOverviewDto
from application.overview.facade import (
    LocationOverviewFacade,
    OverviewLocationNotFoundError,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.overview_repository import (
    OverviewRepository,
)
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/locations",
    tags=["overview"],
)


def get_overview_facade(
    db: Session = Depends(get_db),
) -> LocationOverviewFacade:
    overview_repository = OverviewRepository(db)
    automation_repository = AutomationRepository(db)

    automation_service = AutomationService(
        automation_repository
    )

    return LocationOverviewFacade(
        overview_repository,
        automation_repository,
        automation_service,
    )


@router.get(
    "/{location_id}/overview",
    response_model=LocationOverviewDto,
)
def get_location_overview(
    location_id: UUID,
    facade: LocationOverviewFacade = Depends(
        get_overview_facade
    ),
) -> LocationOverviewDto:
    try:
        return facade.get_overview(location_id)

    except OverviewLocationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
