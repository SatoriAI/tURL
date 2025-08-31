from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, HttpUrl, PositiveInt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from source.database.connection import get_session
from source.database.models import Link
from source.settings import settings

router = APIRouter()


class ExtendRequest(BaseModel):
    lifetime: PositiveInt | None


class LinkInfo(BaseModel):
    url: HttpUrl

    lifetime: PositiveInt | None
    registered: date
    modified: date | None

    expires_at: date
    expires_in: PositiveInt
    expired: bool


def populate_response_schema(link: Link) -> LinkInfo:
    return LinkInfo(
        url=link.url,
        lifetime=link.detail.lifetime,
        registered=link.detail.registered,
        modified=link.detail.modified,
        expires_at=link.detail.expires_at,
        expires_in=link.detail.expires_in,
        expired=link.detail.expired,
    )


@router.get(
    "/info/{code}",
    summary="Extracts information about a link.",
    tags=["Management"],
    response_model=LinkInfo,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "There's no `link` assigned to this code or the link has been already revoked."
        },
    },
)
async def info(request: Request, code: str, db_session: AsyncSession = Depends(get_session)):
    link = await db_session.scalar(select(Link).options(joinedload(Link.detail)).where(Link.code == code))

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There's no `link` assigned to this code or the link has been already revoked.",
        )

    return populate_response_schema(link=link)


@router.patch(
    "/extend/{code}",
    summary="Extends lifetime of an existing link.",
    tags=["Management"],
    response_model=LinkInfo,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "There's no `link` assigned to this code."},
    },
)
async def extend(
    request: Request, code: str, payload: ExtendRequest, db_session: AsyncSession = Depends(get_session)
) -> LinkInfo:
    async with db_session.begin():
        link = await db_session.scalar(
            select(Link).options(joinedload(Link.detail)).where(Link.code == code).with_for_update(of=Link)
        )

        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="There's no `link` assigned to this code."
            )

        if payload.lifetime:
            link.detail.lifetime = (link.detail.lifetime or 0) + payload.lifetime
        else:
            link.detail.lifetime = settings.infinite_lifetime

        await db_session.flush()

    await db_session.refresh(link.detail)

    return populate_response_schema(link=link)
