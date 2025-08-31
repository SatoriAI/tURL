from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, HttpUrl, PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.models import Link

router = APIRouter()


class ExtendRequest(BaseModel):
    lifetime: PositiveInt


class ExtendResponse(BaseModel):
    url: HttpUrl
    expires: PositiveInt


@router.patch("/extend/{code}")
async def extend(
    request: Request, code: str, payload: ExtendRequest, db_session: AsyncSession = Depends(get_session)
) -> ExtendResponse:
    code = str(payload.url).split("/")[-1]

    link = db_session.get(Link, code)

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no `link` assigned to this code.")

    return Response(status_code=status.HTTP_200_OK)
