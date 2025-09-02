from datetime import date, timedelta

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from source.settings import settings


class Base(DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "link"
    __table_args__ = (Index("ix_link_code", "code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    # SQL Alchemy Relations
    detail: Mapped["Detail"] = relationship(back_populates="link", cascade="all, delete-orphan", uselist=False)

    @property
    def encoded(self) -> str:
        return f"{settings.domain}/{self.code}"


class Detail(Base):
    __tablename__ = "detail"
    __table_args__ = (
        CheckConstraint("length > 0", name="ck_detail_length_positive"),
        CheckConstraint("lifetime IS NULL OR lifetime > 0", name="ck_detail_lifetime_positive"),
        Index("ix_detail_link_id", "link_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relations
    link_id: Mapped[int] = mapped_column(ForeignKey("link.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Encoding
    length: Mapped[int] = mapped_column(Integer())  # positive integer

    # Schedule
    lifetime: Mapped[int | None] = mapped_column(Integer())  # positive integer or empty (= infinite lifetime)
    registered: Mapped[date] = mapped_column(Date(), server_default=func.now(), nullable=False)  # pylint: disable=not-callable
    modified: Mapped[date] = mapped_column(Date(), onupdate=func.now(), nullable=True)  # pylint: disable=not-callable

    # SQL Alchemy Relations
    link: Mapped["Link"] = relationship(back_populates="detail")

    @property
    def expires_at(self) -> date | None:
        if self.lifetime is None:
            return None
        return self.registered + timedelta(days=self.lifetime)

    @property
    def expires_in(self) -> int | None:
        if not self.expires_at:
            return None
        return (self.expires_at - date.today()).days

    @property
    def expired(self) -> bool:
        if not self.expires_at:
            return False
        return date.today() > self.expires_at
