from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_throttle import RateLimiter

from source.endpoints.decode import router as decode_router
from source.endpoints.encode import router as encode_router
from source.endpoints.focal import router as focal_router
from source.endpoints.management import router as management_router
from source.endpoints.status import router as status_router
from source.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(
        name="tURL",
        description="Tiny microservice for shortening URLs.",
        docs_url=None,
        redoc_url="/docs",
        dependencies=[
            Depends(RateLimiter(times=settings.rate_limit_requests, seconds=settings.rate_limit_window_seconds)),
        ],
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origins],
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    application.include_router(decode_router)
    application.include_router(encode_router)
    application.include_router(management_router)
    application.include_router(status_router)
    application.include_router(focal_router)

    return application


app = create_app()
