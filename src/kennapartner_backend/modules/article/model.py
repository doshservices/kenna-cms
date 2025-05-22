from beanie import Document, before_event, Insert, Save, Replace
from datetime import datetime, timezone


class Article:
    name: str
    text: str
    author: str
    category: str
    created_at: datetime = None
    updated_at: datetime = None

    class Settings:
        name = "artcles"

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Replace, Save)
    def set_updatd_at(self):
        self.updated_at = datetime.now(timezone.utc)
