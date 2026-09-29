from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from application.locations.config_service import (
    LastZoneDeletionError,
    LocationConfigService,
    LocationNotFoundError,
    ZoneNotFoundError,
)
from application.locations.dto import (
    LocationConfigCreateRequest,
    LocationConfigRead,
    LocationRead,
    ZoneCreateRequest,
    ZoneRead,
    ZoneUpdateRequest,
)
from domain.locations.errors import ConfigurationError
from infrastructure.persistence.location_repository import LocationRepository
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_location_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    repository = LocationRepository(db)
    return LocationConfigService(repository)


@router.post(
    "/config",
    response_model=LocationConfigRead,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: LocationConfigCreateRequest,
    service: LocationConfigService = Depends(get_location_service),
) -> LocationConfigRead:
    try:
        return service.create_config(request)

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[LocationRead],
)
def list_locations(
    service: LocationConfigService = Depends(get_location_service),
) -> list[LocationRead]:
    return service.list_locations()


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigRead,
)
def get_location_config(
    location_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
) -> LocationConfigRead:
    try:
        return service.get_config(location_id)

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
) -> Response:
    try:
        service.delete_location(location_id)

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{location_id}/zones",
    response_model=ZoneRead,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneCreateRequest,
    service: LocationConfigService = Depends(get_location_service),
) -> ZoneRead:
    try:
        return service.add_zone(
            location_id,
            request,
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except LocationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneRead,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneUpdateRequest,
    service: LocationConfigService = Depends(get_location_service),
) -> ZoneRead:
    try:
        return service.update_zone(
            location_id,
            zone_id,
            request,
        )

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except (LocationNotFoundError, ZoneNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(get_location_service),
) -> Response:
    try:
        service.delete_zone(
            location_id,
            zone_id,
        )

    except LastZoneDeletionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except (LocationNotFoundError, ZoneNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )