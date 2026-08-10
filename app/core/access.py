"""Shared scoping rules for organization-owned resources.

Every rule here treats a NULL scope as "matches nothing". Matching NULL against
NULL is what previously let an unscoped ORG_ADMIN reach the unscoped
SUPER_ADMIN row, so the same mistake must not reappear for media or analysis.
"""

from fastapi import HTTPException
from sqlalchemy import false, or_, select

from app.models.enums import UserRole
from app.models.media import Media
from app.models.user import User


def ensure_organization_access(
    current_user: User,
    organization_id: int,
    resource: str = "data"
):

    if current_user.role == UserRole.SUPER_ADMIN:
        return

    if (
        current_user.organization_id is None
        or current_user.organization_id != organization_id
    ):
        raise HTTPException(
            status_code=403,
            detail=f"You can access only your organization's {resource}."
        )


def ensure_team_access(
    current_user: User,
    team,
    resource: str = "data"
):
    """`team` is the Team row, so an ORG_ADMIN can be checked against the
    team's own organization rather than trusting the id in the URL."""

    if current_user.role == UserRole.SUPER_ADMIN:
        return

    if current_user.role == UserRole.ORG_ADMIN:

        ensure_organization_access(
            current_user,
            team.organization_id,
            resource
        )

        return

    if current_user.role != UserRole.TEAM_LEAD:
        raise HTTPException(
            status_code=403,
            detail=f"You don't have permission to access team {resource}."
        )

    if (
        current_user.team_id is None
        or current_user.team_id != team.id
    ):
        raise HTTPException(
            status_code=403,
            detail=f"You can access only your team's {resource}."
        )


def ensure_user_access(
    current_user: User,
    user,
    resource: str = "data"
):
    """Scope check for looking at another user's records."""

    if current_user.role == UserRole.SUPER_ADMIN:
        return

    if current_user.role == UserRole.ORG_ADMIN:

        ensure_organization_access(
            current_user,
            user.organization_id,
            resource
        )

        return

    if current_user.role == UserRole.TEAM_LEAD:

        if (
            current_user.team_id is None
            or user.team_id != current_user.team_id
        ):
            raise HTTPException(
                status_code=403,
                detail=f"You can access only your team's {resource}."
            )

        return

    if current_user.id != user.id:
        raise HTTPException(
            status_code=403,
            detail=f"You can access only your own {resource}."
        )


# is_deleted is nullable in older rows, so isnot(True) rather than == False.
NOT_DELETED = Media.is_deleted.isnot(True)


def media_visibility_filter(current_user: User):
    """SQL predicate limiting Media rows to what current_user may see.

    Returns None for SUPER_ADMIN, meaning "no role restriction" -- soft-deleted
    rows are excluded separately by apply_media_scope, for everyone.
    """

    if current_user.role == UserRole.SUPER_ADMIN:
        return None

    if current_user.role == UserRole.ORG_ADMIN:

        if current_user.organization_id is None:
            return false()

        return Media.organization_id == current_user.organization_id

    if current_user.role == UserRole.TEAM_LEAD:

        if current_user.team_id is None:
            return false()

        team_members = select(User.id).where(
            User.team_id == current_user.team_id
        )

        return or_(
            Media.calling_agent_id.in_(team_members),
            Media.uploaded_by.in_(team_members),
        )

    # AGENT: only calls they made or uploaded themselves
    return or_(
        Media.calling_agent_id == current_user.id,
        Media.uploaded_by == current_user.id,
    )


def apply_media_scope(statement, current_user: User):
    """Apply media_visibility_filter to a select() that already involves Media.

    Single fetches go through this too, so a row the user cannot see simply
    does not come back -- there is no second copy of the rule to drift.
    """

    statement = statement.where(NOT_DELETED)

    condition = media_visibility_filter(current_user)

    if condition is None:
        return statement

    return statement.where(condition)
