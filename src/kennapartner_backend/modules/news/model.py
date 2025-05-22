from beanie import Document, Insert, Replace, Save, before_event
from datetime import datetime, timezone
from typing import Optional


class News(Document):
    title: str
    content: str
    file_url: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    class Settings:
        name = "news"

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Replace, Save)
    def set_updatd_at(self):
        self.updated_at = datetime.now(timezone.utc)
