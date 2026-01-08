from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import uuid


def _serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert database row to JSON-serializable dict."""
    result = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat() if value else None
        elif isinstance(value, uuid.UUID):
            result[key] = str(value)
        else:
            result[key] = value
    return result


class ModelFieldConfigRepository:
    async def list_by_model(self, session: AsyncSession, model_name: str) -> List[Dict[str, Any]]:
        query = text(
            """
            SELECT id, model_name, field_name, field_type, label_key, validators,
                   visibility_rule, required, default_value, description,
                   created_at, updated_at, created_by
            FROM model_field_configurations
            WHERE model_name = :model_name
            ORDER BY field_name
            """
        )
        result = await session.execute(query, {"model_name": model_name})
        rows = result.mappings().all()
        return [_serialize_row(dict(row)) for row in rows]

    async def get_one(self, session: AsyncSession, model_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        query = text(
            """
            SELECT id, model_name, field_name, field_type, label_key, validators,
                   visibility_rule, required, default_value, description,
                   created_at, updated_at, created_by
            FROM model_field_configurations
            WHERE model_name = :model_name AND field_name = :field_name
            """
        )
        result = await session.execute(query, {"model_name": model_name, "field_name": field_name})
        row = result.mappings().first()
        return _serialize_row(dict(row)) if row else None

    async def update_field(
        self,
        session: AsyncSession,
        model_name: str,
        field_name: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        # Build dynamic SET clause
        allowed = {"label_key", "validators", "visibility_rule", "required", "default_value", "description"}
        set_parts = []
        params: Dict[str, Any] = {"model_name": model_name, "field_name": field_name}
        for key, value in updates.items():
            if key in allowed:
                set_parts.append(f"{key} = :{key}")
                params[key] = value

        if not set_parts:
            return await self.get_one(session, model_name, field_name)

        set_clause = ", ".join(set_parts) + ", updated_at = NOW()"
        query = text(
            f"""
            UPDATE model_field_configurations
            SET {set_clause}
            WHERE model_name = :model_name AND field_name = :field_name
            RETURNING id, model_name, field_name, field_type, label_key, validators,
                      visibility_rule, required, default_value, description,
                      created_at, updated_at, created_by
            """
        )
        result = await session.execute(query, params)
        row = result.mappings().first()
        if row:
            await session.commit()
            return _serialize_row(dict(row))
        return None
