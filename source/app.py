from fastapi import FastAPI

from source.endpoints.decode import router as decode_router
from source.endpoints.encode import router as encode_router
from source.endpoints.management import router as info_router
from source.endpoints.status import router as status_router


def create_app() -> FastAPI:
    application = FastAPI(
        name="tURL",
        description="Tiny microservice for shortening URLs.",
        docs_url="/swagger",
        redoc_url="/docs",
    )

    application.include_router(decode_router)
    application.include_router(encode_router)
    application.include_router(info_router)
    application.include_router(status_router)

    return application


app = create_app()
