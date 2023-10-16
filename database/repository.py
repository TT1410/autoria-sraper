from sqlalchemy import exists
from sqlalchemy.orm import Session

from .models import UsedCar


class UsedCarRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def exists_by_url(self, url: str) -> bool:
        return self.session.scalar(
            exists()
            .where(UsedCar.url == url)
            .select()
        )

    def create_car(self, item: dict) -> None:
        self.session.add(UsedCar(**item))

        self.session.commit()
