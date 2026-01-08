from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional
import json
import uuid

router = APIRouter(prefix="/system/translations", tags=["System Translations"])

# Simple in-memory store for translations (will be replaced with database)
# In production, this should use a proper database table
TRANSLATIONS_DB = {}

class TranslationSchema:
    def __init__(self, id: str, key: str, namespace: str, pt_br: str, en_us: str, es_es: str, 
                 created_at: str = None, updated_at: str = None, created_by: str = "system", 
                 updated_by: str = "system"):
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
    result = []
    
    for trans in TRANSLATIONS_DB.values():
        # Filter by search term
        if search:
            search_lower = search.lower()
            if not (search_lower in trans.key.lower() or 
                   search_lower in trans.pt_br.lower() or
                   search_lower in trans.en_us.lower() or
                   search_lower in trans.es_es.lower()):
                continue
        
        # Filter by namespace
        if namespace and trans.namespace != namespace:
            continue
        
        result.append(trans.to_dict())
    
    return result[:limit]


@router.post("")
async def create_translation(
    data: dict,
):
    """
    Create a new translation key.
    """
    key = data.get("key", "").strip()
    namespace = data.get("namespace", "common").strip()
    
    # Validate
    if not key or not all(c.isalnum() or c in "._-" for c in key):
        raise HTTPException(status_code=400, detail="Invalid key format. Use alphanumeric, dots, hyphens, underscores.")
    
    if namespace not in ["common", "ingestion", "wave2", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid namespace")
    
    pt_br = data.get("pt_br", "").strip()
    en_us = data.get("en_us", "").strip()
    es_es = data.get("es_es", "").strip()
    
    if not all([pt_br, en_us, es_es]):
        raise HTTPException(status_code=400, detail="All translations are required")
    
    # Check if key already exists
    composite_key = f"{namespace}:{key}"
    if composite_key in TRANSLATIONS_DB:
        raise HTTPException(status_code=409, detail="Translation key already exists")
    
    # Create translation
    trans = TranslationSchema(
        id=composite_key,
        key=key,
        namespace=namespace,
        pt_br=pt_br,
        en_us=en_us,
        es_es=es_es,
        created_by="system",
        updated_by="system",
    )
    
    TRANSLATIONS_DB[composite_key] = trans
    
    return trans.to_dict()


@router.patch("/{translation_id}")
async def update_translation(
    translation_id: str,
    data: dict,
):
    """
    Update a translation key.
    """
    if translation_id not in TRANSLATIONS_DB:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    trans = TRANSLATIONS_DB[translation_id]
    
    # Update fields
    if "pt_br" in data and data["pt_br"]:
        trans.pt_br = data["pt_br"].strip()
    if "en_us" in data and data["en_us"]:
        trans.en_us = data["en_us"].strip()
    if "es_es" in data and data["es_es"]:
        trans.es_es = data["es_es"].strip()
    
    trans.updated_at = datetime.utcnow().isoformat()
    trans.updated_by = "system"
    
    return trans.to_dict()


@router.delete("/{translation_id}")
async def delete_translation(
    translation_id: str,
):
    """
    Delete a translation key.
    """
    if translation_id not in TRANSLATIONS_DB:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    del TRANSLATIONS_DB[translation_id]
    
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
                    created_by=current_user.get("sub", "system"),
                    updated_by=current_user.get("sub", "system"),
                )
                TRANSLATIONS_DB[composite_key] = trans
                imported_count += 1
            else:
                # Update existing
                trans = TRANSLATIONS_DB[composite_key]
                trans.pt_br = pt_br.get(namespace, {}).get(key, trans.pt_br)
                trans.en_us = en_us.get(namespace, {}).get(key, trans.en_us)
                trans.es_es = es_es.get(namespace, {}).get(key, trans.es_es)
                trans.updated_by = current_user.get("sub", "system")
                trans.updated_at = datetime.utcnow().isoformat()
    
    return {
        "message": f"Import completed",
        "imported": imported_count,
        "total": len(TRANSLATIONS_DB),
    }
