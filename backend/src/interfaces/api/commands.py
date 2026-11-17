
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from application.commands.dto import (
    CommandLogDto,
    CommandRequestDto,
)
from application.commands.service import (
    CommandDeviceNotFoundError,
    CommandService,
)
from domain.commands.invoker import UnknownCommandError
from infrastructure.persistence.session import get_db


router = APIRouter(
    prefix="/api/commands",
    tags=["commands"],
)


@router.post(
    "",
    response_model=CommandLogDto,
    responses={
        400: {"description": "Unknown command type"},
        404: {"description": "Actuator not found"},
        409: {
            "description": "Command rejected by state guard",
            "model": CommandLogDto,
        },
    },
    summary="Execute an actuator command",
)
def execute_command(
    request: CommandRequestDto,
    db: Session = Depends(get_db),
):
    service = CommandService(db)

    try:
        row = service.execute(
            command_type=request.command_type,
            device_id=request.device_id,
            payload=request.payload,
        )

    except CommandDeviceNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except UnknownCommandError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    result = CommandLogDto.model_validate(row)

    # A rejected command returns the saved log row,
    # not an ordinary HTTPException detail object.
    if result.status == "rejected":
        return JSONResponse(
            status_code=409,
            content=jsonable_encoder(result),
        )

    # Success and execution failure both return 200.
    return result


@router.get(
    "",
    response_model=list[CommandLogDto],
    summary="List recent actuator commands",
)
def list_commands(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = CommandService(db)

    rows = service.list_recent(limit)

    return [
        CommandLogDto.model_validate(row)
        for row in rows
    ]
