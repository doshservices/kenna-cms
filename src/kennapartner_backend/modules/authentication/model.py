from beanie import Document, Indexed, before_event, Insert, Replace, Save
from typing import Annotated
from datetime import datetime, timezone


class User(Document):
    username: Annotated[str, Indexed(unique=True)]
    password: str
    created_at: datetime = None
    updated_at: datetime = None

    class Settings:
        name = "users"

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Replace, Save)
    def set_updatd_at(self):
        self.updated_at = datetime.now(timezone.utc)
