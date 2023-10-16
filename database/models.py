from datetime import datetime
from typing import Optional

from sqlalchemy import func, String, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UsedCar(Base):
    __tablename__ = "used_cars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(500), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(500))
    price_usd: Mapped[int] = mapped_column(BIGINT)
    odometer: Mapped[Optional[int]] = mapped_column(BIGINT)
    username: Mapped[Optional[str]] = mapped_column(String(500))
    phone_number: Mapped[int] = mapped_column(BIGINT)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    images_count: Mapped[int] = mapped_column()
    car_number: Mapped[Optional[str]] = mapped_column(String(20))
    car_vin: Mapped[str] = mapped_column(String(100))
    datetime_found: Mapped[datetime] = mapped_column(default=func.now())
