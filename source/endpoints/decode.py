from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.models import Link

router = APIRouter()


@router.get(
    "/d/{code}",
    summary="Redirects to the original URL.",
    tags=["Encryption"],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
    responses={
        status.HTTP_308_PERMANENT_REDIRECT: {"description": "Successful redirection to the original URL."},
        status.HTTP_404_NOT_FOUND: {"description": "There's no `link` assigned to this code."},
    },
)
# pylint: disable=unused-argument
async def decode(request: Request, code: str, db_session: AsyncSession = Depends(get_session)) -> RedirectResponse:
    url = await db_session.scalar(select(Link.url).where(Link.code == code))

    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no `link` assigned to this code.")

    return RedirectResponse(status_code=status.HTTP_308_PERMANENT_REDIRECT, url=url)
