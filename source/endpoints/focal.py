from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from source.settings import settings

router = APIRouter()


@router.get("/", summary="Redirects to frontend.", status_code=status.HTTP_308_PERMANENT_REDIRECT)
async def home(request: Request) -> RedirectResponse:  # pylint: disable=unused-argument
    return RedirectResponse(status_code=status.HTTP_308_PERMANENT_REDIRECT, url=settings.frontend)
