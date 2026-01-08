from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.postgres.connection import get_session
from app.infrastructure.repositories.model_field_config_repository import (
    ModelFieldConfigRepository,
)
from app.interfaces.http.routers.acl import require_acl

router = APIRouter()


class FieldConfig(BaseModel):
    id: str  # UUID as string
    model_name: str
    field_name: str
    field_type: str
    label_key: Optional[str] = None
    validators: Optional[Dict[str, Any]] = None
    visibility_rule: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[Any] = None
    description: Optional[str] = None
    created_at: Optional[str] = None  # ISO format string
    updated_at: Optional[str] = None  # ISO format string
    created_by: Optional[str] = None


class UpdateFieldConfigRequest(BaseModel):
    label_key: Optional[str] = Field(None, description="Translation key for label")
    validators: Optional[Dict[str, Any]] = Field(None, description="JSON schema validators")
    visibility_rule: Optional[str] = Field(None, description="Visibility rule expression")
    required: Optional[bool] = None
    default_value: Optional[Any] = None
    description: Optional[str] = None


@router.get(
    "/model-configs/{model}",
    response_model=List[FieldConfig],
    summary="List field configurations for a model",
    dependencies=[Depends(require_acl("model_config", "read"))],
)
async def list_model_configs(
    model: str, session: AsyncSession = Depends(get_session)
) -> List[FieldConfig]:
    repo = ModelFieldConfigRepository()
    rows = await repo.list_by_model(session, model)
    return [FieldConfig(**row) for row in rows]


@router.patch(
    "/model-configs/{model}/{field}",
    response_model=FieldConfig,
    summary="Update a field configuration",
    dependencies=[Depends(require_acl("model_config", "update"))],
)
async def update_model_field_config(
    model: str,
    field: str,
    body: UpdateFieldConfigRequest,
    session: AsyncSession = Depends(get_session),
) -> FieldConfig:
    repo = ModelFieldConfigRepository()
    updated = await repo.update_field(session, model, field, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field config not found")
    return FieldConfig(**updated)
