from beanie import Document, Insert, Replace, Save, before_event, Link
from datetime import datetime, timezone
from typing import Optional, Annotated, List
from pydantic import Field


class InsightAuthor(Document):
    full_name: str
    email: str
    file_url: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    class Settings:
        name = "insight_authors"
        
    
    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Replace, Save)
    def set_updatd_at(self):
        self.updated_at = datetime.now(timezone.utc)



class Insight(Document):
    title: str
    content: str
    file_url: Optional[str] = None
    authors: Annotated[List[Link[InsightAuthor]], Field(description="List of authors")]
    created_at: datetime = None
    updated_at: datetime = None

    class Settings:
        name = "insights"

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Replace, Save)
    def set_updatd_at(self):
        self.updated_at = datetime.now(timezone.utc)
