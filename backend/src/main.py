import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from application.readings.sampler import ReadingSampler
from application.readings.service import ReadingIngest
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository
from infrastructure.persistence.session import SessionLocal
from infrastructure.settings import settings
from interfaces.api.health import router as health_router
from interfaces.api.sensors import router as sensors_router
from interfaces.api.devices import router as devices_router
from interfaces.api.locations import router as locations_router


async def sampling_loop() -> None:
    while True:
        db = SessionLocal()

        try:
            device_repository = DeviceRepository(db)
            reading_repository = ReadingRepository(db)

            reading_ingest = ReadingIngest(
                device_repository,
                reading_repository,
            )

            sampler = ReadingSampler(
                device_repository,
                reading_repository,
                reading_ingest,
            )

            sampler.run_once()

        except Exception as error:
            print(
                f"Background sampler error: {error}"
            )

        finally:
            db.close()

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sampler_task = asyncio.create_task(
        sampling_loop()
    )

    yield

    sampler_task.cancel()

    try:
        await sampler_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(locations_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Smart Greenhouse API",
        "scalar": "/scalar",
        "openapi": "/openapi.json",
    }


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url or "/openapi.json",
        title="Smart Greenhouse API",
    )