import pytest
from datetime import datetime
from outstanding_projects import Project, ProjectRegistry, ProjectStatus


def make_project(**kwargs) -> Project:
    defaults = {"title": "Test Project", "owner": "alexander.swift"}
    return Project(**{**defaults, **kwargs})


class TestProjectStatus:
    def test_new_project_is_draft(self):
        p = make_project()
        assert p.is_draft()
        assert p.status == ProjectStatus.DRAFT

    def test_publish_moves_draft_to_outstanding(self):
        p = make_project()
        p.publish()
        assert p.is_outstanding()
        assert p.status == ProjectStatus.OUTSTANDING

    def test_cannot_publish_non_draft(self):
        p = make_project()
        p.publish()
        with pytest.raises(ValueError, match="Only draft projects can be published"):
            p.publish()

    def test_complete_moves_outstanding_to_completed(self):
        p = make_project()
        p.publish()
        p.complete()
        assert p.status == ProjectStatus.COMPLETED

    def test_cannot_complete_draft(self):
        p = make_project()
        with pytest.raises(ValueError, match="Only outstanding projects can be completed"):
            p.complete()

    def test_cancel_draft(self):
        p = make_project()
        p.cancel()
        assert p.status == ProjectStatus.CANCELLED

    def test_cancel_outstanding(self):
        p = make_project()
        p.publish()
        p.cancel()
        assert p.status == ProjectStatus.CANCELLED

    def test_cannot_cancel_completed(self):
        p = make_project()
        p.publish()
        p.complete()
        with pytest.raises(ValueError, match="Cannot cancel a completed project"):
            p.cancel()

    def test_publish_updates_timestamp(self):
        p = make_project()
        before = p.updated_at
        p.publish()
        assert p.updated_at >= before


class TestProjectRegistry:
    def setup_method(self):
        self.registry = ProjectRegistry()

    def test_add_and_get_project(self):
        p = make_project(title="Alpha")
        self.registry.add(p)
        assert self.registry.get(p.id) == p

    def test_get_nonexistent_returns_none(self):
        assert self.registry.get("nonexistent") is None

    def test_get_all_outstanding(self):
        draft = make_project(title="Draft")
        outstanding = make_project(title="Outstanding")
        outstanding.publish()

        self.registry.add(draft)
        self.registry.add(outstanding)

        result = self.registry.get_all_outstanding()
        assert outstanding in result
        assert draft not in result

    def test_get_all_drafts(self):
        draft = make_project(title="Draft")
        outstanding = make_project(title="Outstanding")
        outstanding.publish()

        self.registry.add(draft)
        self.registry.add(outstanding)

        result = self.registry.get_all_drafts()
        assert draft in result
        assert outstanding not in result

    def test_get_by_owner(self):
        p1 = make_project(owner="alexander.swift")
        p2 = make_project(owner="other.user")
        self.registry.add(p1)
        self.registry.add(p2)

        result = self.registry.get_by_owner("alexander.swift")
        assert p1 in result
        assert p2 not in result

    def test_get_outstanding_by_owner(self):
        draft = make_project(owner="alexander.swift", title="Draft")
        outstanding = make_project(owner="alexander.swift", title="Outstanding")
        outstanding.publish()
        other = make_project(owner="other.user", title="Other")
        other.publish()

        self.registry.add(draft)
        self.registry.add(outstanding)
        self.registry.add(other)

        result = self.registry.get_outstanding_by_owner("alexander.swift")
        assert outstanding in result
        assert draft not in result
        assert other not in result

    def test_remove_project(self):
        p = make_project()
        self.registry.add(p)
        assert self.registry.remove(p.id) is True
        assert self.registry.get(p.id) is None

    def test_remove_nonexistent_returns_false(self):
        assert self.registry.remove("nonexistent") is False
