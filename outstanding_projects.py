from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ProjectStatus(Enum):
    DRAFT = "draft"
    OUTSTANDING = "outstanding"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Project:
    title: str
    owner: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None

    def publish(self) -> None:
        if self.status != ProjectStatus.DRAFT:
            raise ValueError(f"Only draft projects can be published, current status: {self.status.value}")
        self.status = ProjectStatus.OUTSTANDING
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        if self.status != ProjectStatus.OUTSTANDING:
            raise ValueError(f"Only outstanding projects can be completed, current status: {self.status.value}")
        self.status = ProjectStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        if self.status in (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED):
            raise ValueError(f"Cannot cancel a {self.status.value} project")
        self.status = ProjectStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def is_outstanding(self) -> bool:
        return self.status == ProjectStatus.OUTSTANDING

    def is_draft(self) -> bool:
        return self.status == ProjectStatus.DRAFT


class ProjectRegistry:
    def __init__(self):
        self._projects: dict[str, Project] = {}

    def add(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    def get(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)

    def get_all_outstanding(self) -> list[Project]:
        return [p for p in self._projects.values() if p.is_outstanding()]

    def get_all_drafts(self) -> list[Project]:
        return [p for p in self._projects.values() if p.is_draft()]

    def get_by_owner(self, owner: str) -> list[Project]:
        return [p for p in self._projects.values() if p.owner == owner]

    def get_outstanding_by_owner(self, owner: str) -> list[Project]:
        return [p for p in self._projects.values() if p.is_outstanding() and p.owner == owner]

    def remove(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False
