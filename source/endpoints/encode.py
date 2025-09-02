from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, HttpUrl, PositiveInt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.models import Detail, Link
from source.settings import settings
from source.utils.functions import code

router = APIRouter()


class EncodeRequest(BaseModel):
    url: HttpUrl
    lifetime: PositiveInt | None
    length: PositiveInt


class EncodeResponse(BaseModel):
    url: HttpUrl


@router.post(
    "/encode",
    summary="Encodes a long URL into a short one.",
    tags=["Encryption"],
    response_model=EncodeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Could not generate a unique code. Try again or increase `length`."
        }
    },
)
async def encode(  # pylint: disable=unused-argument
    request: Request, payload: EncodeRequest, db_session: AsyncSession = Depends(get_session)
) -> EncodeResponse:
    for _ in range(settings.max_code_generation_attempts):  # Cheaper than making a database call
        candidate = code(length=payload.length)

        link = Link(
            url=str(payload.url), code=candidate, detail=Detail(length=payload.length, lifetime=payload.lifetime)
        )

        async with db_session.begin():
            db_session.add(link)

            try:
                await db_session.flush()
                return EncodeResponse(url=HttpUrl(link.encoded))
            except IntegrityError:
                await db_session.rollback()

    # Exhausted all attempts to generate a unique short code.
    # Consider increasing the 'length' parameter to expand the available code space.
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Could not generate a unique code. Try again or increase `length`.",
    )
