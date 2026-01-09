from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/translations", tags=["System Translations"])

# Simple in-memory store for translations (will be replaced with database)
# In production, this should use a proper database table
TRANSLATIONS_DB = {}


class TranslationSchema:
    def __init__(
        self,
        id: str,
        key: str,
        namespace: str,
        pt_br: str,
        en_us: str,
        es_es: str,
        created_at: str = None,
        updated_at: str = None,
        created_by: str = "system",
        updated_by: str = "system",
    ):
        self.id = id
        self.key = key
        self.namespace = namespace
        self.pt_br = pt_br
        self.en_us = en_us
        self.es_es = es_es
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.created_by = created_by
        self.updated_by = updated_by

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "namespace": self.namespace,
            "pt_br": self.pt_br,
            "en_us": self.en_us,
            "es_es": self.es_es,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }


@router.get("", response_model=List[dict])
async def get_translations(
    search: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
):
    """
    Get all translations with optional filtering.
    """
    from sqlalchemy import create_engine, text
    from app.infrastructure.config.settings import Settings
    
    settings = Settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        query = "SELECT * FROM translations WHERE 1=1"
        params = {}
        
        if search:
            query += " AND (key ILIKE :search OR pt_br ILIKE :search OR en_us ILIKE :search OR es_es ILIKE :search)"
            params['search'] = f"%{search}%"
        
        if namespace:
            query += " AND namespace = :namespace"
            params['namespace'] = namespace
        
        query += f" LIMIT :limit"
        params['limit'] = limit
        
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        
        translations = []
        for row in rows:
            translations.append({
                'id': row[0],
                'key': row[1],
                'namespace': row[2],
                'pt_br': row[3],
                'en_us': row[4],
                'es_es': row[5],
                'created_at': row[6].isoformat() if row[6] else None,
                'updated_at': row[7].isoformat() if row[7] else None,
                'created_by': row[8],
                'updated_by': row[9]
            })
        
        return translations


@router.post("")
async def create_translation(
    data: dict,
):
    """
    Create a new translation key.
    """
    from sqlalchemy import create_engine, text
    from datetime import datetime
    from app.infrastructure.config.settings import Settings
    
    key = data.get("key", "").strip()
    namespace = data.get("namespace", "common").strip()
    pt_br = data.get("pt_br", "").strip()
    en_us = data.get("en_us", "").strip()
    es_es = data.get("es_es", "").strip()
    
    if not key or not all(c.isalnum() or c in "._-" for c in key):
        raise HTTPException(
            status_code=400,
            detail="Invalid key format. Use alphanumeric, dots, hyphens, underscores.",
        )
    if namespace not in ["common", "ingestion", "wave2", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid namespace")
    if not all([pt_br, en_us, es_es]):
        raise HTTPException(status_code=400, detail="All translations are required")
    
    settings = Settings()
    engine = create_engine(settings.database_url)
    
    translation_id = f"{namespace}:{key}"
    now = datetime.utcnow()
    
    with engine.connect() as conn:
        # Check if exists
        check_query = text("SELECT COUNT(*) FROM translations WHERE id = :id")
        result = conn.execute(check_query, {'id': translation_id})
        if result.scalar() > 0:
            raise HTTPException(status_code=409, detail="Translation key already exists")
        
        # Insert
        insert_query = text("""
            INSERT INTO translations (id, key, namespace, pt_br, en_us, es_es, created_at, updated_at, created_by, updated_by)
            VALUES (:id, :key, :namespace, :pt_br, :en_us, :es_es, :created_at, :updated_at, :created_by, :updated_by)
        """)
        conn.execute(insert_query, {
            'id': translation_id,
            'key': key,
            'namespace': namespace,
            'pt_br': pt_br,
            'en_us': en_us,
            'es_es': es_es,
            'created_at': now,
            'updated_at': now,
            'created_by': 'system',
            'updated_by': 'system'
        })
        conn.commit()
        
        return {
            'id': translation_id,
            'key': key,
            'namespace': namespace,
            'pt_br': pt_br,
            'en_us': en_us,
            'es_es': es_es,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'created_by': 'system',
            'updated_by': 'system'
        }


@router.patch("/{translation_id}")
async def update_translation(
    translation_id: str,
    data: dict,
):
    """
    Update a translation key.
    """
    from sqlalchemy import create_engine, text
    from datetime import datetime
    from app.infrastructure.config.settings import Settings
    
    settings = Settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if exists
        check_query = text("SELECT * FROM translations WHERE id = :id")
        result = conn.execute(check_query, {'id': translation_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Translation not found")
        
        # Build update query
        updates = []
        params = {'id': translation_id, 'updated_at': datetime.utcnow()}
        
        if 'pt_br' in data and data['pt_br']:
            updates.append("pt_br = :pt_br")
            params['pt_br'] = data['pt_br']
        if 'en_us' in data and data['en_us']:
            updates.append("en_us = :en_us")
            params['en_us'] = data['en_us']
        if 'es_es' in data and data['es_es']:
            updates.append("es_es = :es_es")
            params['es_es'] = data['es_es']
        
        updates.append("updated_at = :updated_at")
        updates.append("updated_by = 'system'")
        
        update_query = text(f"UPDATE translations SET {', '.join(updates)} WHERE id = :id")
        conn.execute(update_query, params)
        conn.commit()
        
        # Fetch updated row
        result = conn.execute(check_query, {'id': translation_id})
        row = result.fetchone()
        
        return {
            'id': row[0],
            'key': row[1],
            'namespace': row[2],
            'pt_br': row[3],
            'en_us': row[4],
            'es_es': row[5],
            'created_at': row[6].isoformat() if row[6] else None,
            'updated_at': row[7].isoformat() if row[7] else None,
            'created_by': row[8],
            'updated_by': row[9]
        }


@router.delete("/{translation_id}")
async def delete_translation(
    translation_id: str,
):
    """
    Delete a translation key.
    """
    from sqlalchemy import create_engine, text
    from app.infrastructure.config.settings import Settings
    
    settings = Settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if exists
        check_query = text("SELECT COUNT(*) FROM translations WHERE id = :id")
        result = conn.execute(check_query, {'id': translation_id})
        if result.scalar() == 0:
            raise HTTPException(status_code=404, detail="Translation not found")
        
        # Delete
        delete_query = text("DELETE FROM translations WHERE id = :id")
        conn.execute(delete_query, {'id': translation_id})
        conn.commit()
        
        return {"message": "Translation deleted"}


@router.post("/export")
async def export_translations(
    namespace: Optional[str] = Query(None),
):
    """
    Export translations as JSON files organized by namespace and language.
    """
    export_data = {
        "pt-BR": {},
        "en-US": {},
        "es-ES": {},
    }

    for trans in TRANSLATIONS_DB.values():
        if namespace and trans.namespace != namespace:
            continue

        # Create namespace key if not exists
        if trans.namespace not in export_data["pt-BR"]:
            export_data["pt-BR"][trans.namespace] = {}
            export_data["en-US"][trans.namespace] = {}
            export_data["es-ES"][trans.namespace] = {}

        export_data["pt-BR"][trans.namespace][trans.key] = trans.pt_br
        export_data["en-US"][trans.namespace][trans.key] = trans.en_us
        export_data["es-ES"][trans.namespace][trans.key] = trans.es_es

    return export_data


@router.post("/import")
async def import_translations(
    data: dict,
):
    """
    Import translations from JSON structure.
    Expected format:
    {
        "pt-BR": { "namespace": { "key": "value" } },
        "en-US": { "namespace": { "key": "value" } },
        "es-ES": { "namespace": { "key": "value" } }
    }
    """
    pt_br = data.get("pt-BR", {})
    en_us = data.get("en-US", {})
    es_es = data.get("es-ES", {})

    imported_count = 0

    for namespace, keys in pt_br.items():
        for key, value in keys.items():
            composite_key = f"{namespace}:{key}"

            if composite_key not in TRANSLATIONS_DB:
                trans = TranslationSchema(
                    id=composite_key,
                    key=key,
                    namespace=namespace,
                    pt_br=pt_br.get(namespace, {}).get(key, ""),
                    en_us=en_us.get(namespace, {}).get(key, ""),
                    es_es=es_es.get(namespace, {}).get(key, ""),
                    created_by="system",
                    updated_by="system",
                )
                TRANSLATIONS_DB[composite_key] = trans
                imported_count += 1
            else:
                # Update existing
                trans = TRANSLATIONS_DB[composite_key]
                trans.pt_br = pt_br.get(namespace, {}).get(key, trans.pt_br)
                trans.en_us = en_us.get(namespace, {}).get(key, trans.en_us)
                trans.es_es = es_es.get(namespace, {}).get(key, trans.es_es)
                trans.updated_by = "system"
                trans.updated_at = datetime.utcnow().isoformat()

    return {
        "message": "Import completed",
        "imported": imported_count,
        "total": len(TRANSLATIONS_DB),
    }
