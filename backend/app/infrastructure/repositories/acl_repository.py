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


class ACLRepository:
    async def is_allowed(self, session: AsyncSession, roles: List[str], resource: str, action: str) -> bool:
        if not roles:
            return False
        query = text(
            """
            SELECT 1
            FROM acl_rules
            WHERE role = ANY(:roles) AND resource = :resource AND action = :action
            LIMIT 1
            """
        )
        # SQLAlchemy asyncpg requires list to be passed as array
        params = {"roles": roles, "resource": resource, "action": action}
        result = await session.execute(query, params)
        return result.first() is not None

    async def list_rules(self, session: AsyncSession) -> List[Dict[str, Any]]:
        res = await session.execute(text(
            """SELECT id, role, resource, action, condition, description, created_at, updated_at, created_by
                 FROM acl_rules ORDER BY role, resource, action"""
        ))
        return [_serialize_row(dict(r)) for r in res.mappings().all()]

    async def create_rule(self, session: AsyncSession, data: Dict[str, Any]) -> Dict[str, Any]:
        res = await session.execute(text(
            """
            INSERT INTO acl_rules (id, role, resource, action, condition, description)
            VALUES (gen_random_uuid(), :role, :resource, :action, :condition, :description)
            RETURNING id, role, resource, action, condition, description, created_at, updated_at, created_by
            """
        ), data)
        row = res.mappings().first()
        await session.commit()
        return _serialize_row(dict(row))

    async def update_rule(self, session: AsyncSession, rule_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        set_parts = []
        params: Dict[str, Any] = {"id": rule_id}
        for key in ("role", "resource", "action", "condition", "description"):
            if key in data:
                set_parts.append(f"{key} = :{key}")
                params[key] = data[key]
        if not set_parts:
            res = await session.execute(text(
                "SELECT id, role, resource, action, condition, description, created_at, updated_at, created_by FROM acl_rules WHERE id = :id"
            ), params)
            row = res.mappings().first()
            return _serialize_row(dict(row)) if row else None
        set_clause = ", ".join(set_parts) + ", updated_at = NOW()"
        res = await session.execute(text(
            f"""
            UPDATE acl_rules SET {set_clause} WHERE id = :id
            RETURNING id, role, resource, action, condition, description, created_at, updated_at, created_by
            """
        ), params)
        row = res.mappings().first()
        if row:
            await session.commit()
            return _serialize_row(dict(row))
        return None

    async def delete_rule(self, session: AsyncSession, rule_id: str) -> bool:
        res = await session.execute(text("DELETE FROM acl_rules WHERE id = :id"), {"id": rule_id})
        await session.commit()
        # rowcount may not be reliable across drivers, but attempt
        return res.rowcount and res.rowcount > 0
