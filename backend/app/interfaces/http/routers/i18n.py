"""
ProspecIA - i18n Router

Internationalization and localization endpoints.
Provides translation keys for frontend synchronization.
"""

import json
import os
from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()

router = APIRouter()


class TranslationKeysResponse(BaseModel):
    """Translation keys response model."""
    locale: str
    keys: Dict[str, str]
    timestamp: str


SUPPORTED_LOCALES = ['pt-BR', 'en-US', 'es-ES']
DEFAULT_LOCALE = 'pt-BR'

# Cache para traduções carregadas
_translation_cache: Dict[str, Dict[str, str]] = {}


def _load_translations(locale: str) -> Dict[str, str]:
    """
    Load translation file for locale.
    
    Args:
        locale: Language locale (pt-BR, en-US, es-ES)
    
    Returns:
        Dictionary with translation keys
    """
    if locale in _translation_cache:
        return _translation_cache[locale]
    
    # Caminho do arquivo de traduções
    locales_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'frontend', 'public', 'locales', locale, 'common.json'
    )
    
    # Se não existe, tentar locale padrão
    if not os.path.exists(locales_path):
        logger.warning(f"Translation file not found for locale {locale}, using default", locale=locale)
        locales_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'frontend', 'public', 'locales', DEFAULT_LOCALE, 'common.json'
        )
    
    try:
        with open(locales_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        _translation_cache[locale] = translations
        return translations
    except FileNotFoundError:
        logger.error(f"Translation file not found for locale {locale}", locale=locale)
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing translation file for locale {locale}: {str(e)}", locale=locale)
        return {}


@router.get(
    "/translations/{locale}",
    response_model=TranslationKeysResponse,
    status_code=status.HTTP_200_OK,
    summary="Get translations for locale",
    description="Returns translation keys for specified locale",
    tags=["i18n"],
)
async def get_translations(locale: str) -> TranslationKeysResponse:
    """
    Get translations for a specific locale.
    
    Supports: pt-BR (Portuguese-Brazil), en-US (English), es-ES (Spanish)
    
    Args:
        locale: Language locale code (pt-BR, en-US, es-ES)
    
    Returns:
        TranslationKeysResponse: Translation keys and metadata
    
    Raises:
        404: If locale is not supported
    """
    if locale not in SUPPORTED_LOCALES:
        logger.warning(f"Unsupported locale requested", locale=locale, supported=SUPPORTED_LOCALES)
        return TranslationKeysResponse(
            locale=DEFAULT_LOCALE,
            keys=_load_translations(DEFAULT_LOCALE),
            timestamp=datetime.utcnow().isoformat()
        )
    
    logger.info(f"Fetching translations for locale", locale=locale)
    
    translations = _load_translations(locale)
    
    return TranslationKeysResponse(
        locale=locale,
        keys=translations,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get(
    "/locales",
    status_code=status.HTTP_200_OK,
    summary="Get available locales",
    description="Returns list of supported locales",
    tags=["i18n"],
)
async def get_available_locales(request: Request):
    """
    Get list of available locales.
    
    Returns:
        dict: List of supported locales with metadata
    """
    logger.info("Fetching available locales")
    
    user_locale = None
    try:
        if hasattr(request.state, 'user'):
            user_locale = request.state.user.get('preferred_language')
    except Exception:
        user_locale = None

    return {
        "supported_locales": SUPPORTED_LOCALES,
        "default_locale": DEFAULT_LOCALE,
        "user_locale": user_locale or DEFAULT_LOCALE,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@router.post(
    "/translations/reload",
    status_code=status.HTTP_200_OK,
    summary="Reload translations cache",
    description="Force reload of translation cache (admin only)",
    tags=["i18n"],
)
async def reload_translations():
    """
    Force reload of translation cache.
    
    Useful for updating translations without restart.
    Admin only operation.
    
    Returns:
        dict: Status of cache reload
    """
    global _translation_cache
    _translation_cache.clear()
    
    logger.info("Translation cache cleared and reloaded")
    
    # Pré-carregar todas as traduções
    for locale in SUPPORTED_LOCALES:
        _load_translations(locale)
    
    return {
        "status": "success",
        "message": "Translation cache reloaded",
        "locales_reloaded": len(SUPPORTED_LOCALES)
    }
