from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.postgres.connection import get_session
from app.infrastructure.middleware.auth_middleware import get_current_user, require_roles
from app.infrastructure.repositories.acl_repository import ACLRepository

router = APIRouter()


class ACLRule(BaseModel):
    id: str
    role: str
    resource: str
    action: str
    condition: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


class CreateACLRuleRequest(BaseModel):
    role: str
    resource: str
    action: str
    condition: Optional[str] = None
    description: Optional[str] = None


class UpdateACLRuleRequest(BaseModel):
    role: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    condition: Optional[str] = None
    description: Optional[str] = None


@router.get(
    "/acl/rules",
    response_model=List[ACLRule],
    summary="List ACL rules",
    dependencies=[Depends(require_roles("admin"))],
)
async def list_acl_rules(session: AsyncSession = Depends(get_session)) -> List[ACLRule]:
    repo = ACLRepository()
    rows = await repo.list_rules(session)
    return [ACLRule(**r) for r in rows]


@router.post(
    "/acl/rules",
    response_model=ACLRule,
    status_code=status.HTTP_201_CREATED,
    summary="Create ACL rule",
    dependencies=[Depends(require_roles("admin"))],
)
async def create_acl_rule(
    body: CreateACLRuleRequest,
    session: AsyncSession = Depends(get_session),
) -> ACLRule:
    repo = ACLRepository()
    created = await repo.create_rule(session, body.model_dump())
    return ACLRule(**created)


@router.patch(
    "/acl/rules/{rule_id}",
    response_model=ACLRule,
    summary="Update ACL rule",
    dependencies=[Depends(require_roles("admin"))],
)
async def update_acl_rule(
    rule_id: str,
    body: UpdateACLRuleRequest,
    session: AsyncSession = Depends(get_session),
) -> ACLRule:
    repo = ACLRepository()
    updated = await repo.update_rule(session, rule_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return ACLRule(**updated)


@router.delete(
    "/acl/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ACL rule",
    dependencies=[Depends(require_roles("admin"))],
)
async def delete_acl_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = ACLRepository()
    ok = await repo.delete_rule(session, rule_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return None


def require_acl(resource: str, action: str):
    async def checker(request: Request, session: AsyncSession = Depends(get_session)):
        user = get_current_user(request)
        roles = user.get("roles", [])
        repo = ACLRepository()
        allowed = await repo.is_allowed(session, roles, resource, action)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return True

    return checker


@router.get(
    "/acl/check",
    summary="Check if current user is allowed for resource/action",
)
async def acl_check(
    resource: str,
    action: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user = get_current_user(request)
    roles = user.get("roles", [])
    repo = ACLRepository()
    allowed = await repo.is_allowed(session, roles, resource, action)
    return {"allowed": bool(allowed)}
