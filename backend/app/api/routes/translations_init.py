"""
Initialize default translations into the in-memory database when the API starts.
This ensures the application has all necessary translation keys from the beginning.
"""

from datetime import datetime
from app.api.routes.translations import TranslationSchema, TRANSLATIONS_DB

def initialize_default_translations():
    """
    Load default translations from JSON files and populate the in-memory database.
    This is called during application startup.
    """
    
    # Define default translations for all namespaces
    DEFAULT_TRANSLATIONS = [
        # Common translations
        {
            "key": "app.title",
            "namespace": "common",
            "pt_br": "ProspecIA",
            "en_us": "ProspecIA",
            "es_es": "ProspecIA",
        },
        {
            "key": "app.description",
            "namespace": "common",
            "pt_br": "Sistema Inteligente de Prospecção e Gestão de Pesquisas com IA Responsável",
            "en_us": "Intelligent Research Prospecting and Management System with Responsible AI",
            "es_es": "Sistema Inteligente de Prospección y Gestión de Investigación con IA Responsable",
        },
        {
            "key": "nav.home",
            "namespace": "common",
            "pt_br": "Início",
            "en_us": "Home",
            "es_es": "Inicio",
        },
        {
            "key": "nav.dashboard",
            "namespace": "common",
            "pt_br": "Dashboard",
            "en_us": "Dashboard",
            "es_es": "Panel de Control",
        },
        {
            "key": "nav.admin",
            "namespace": "common",
            "pt_br": "Administração",
            "en_us": "Administration",
            "es_es": "Administración",
        },
        {
            "key": "nav.analytics",
            "namespace": "common",
            "pt_br": "Analítica",
            "en_us": "Analytics",
            "es_es": "Analítica",
        },
        # Admin translations
        {
            "key": "translations.title",
            "namespace": "admin",
            "pt_br": "Administração de Traduções",
            "en_us": "Translation Management",
            "es_es": "Gestión de Traducciones",
        },
        {
            "key": "translations.description",
            "namespace": "admin",
            "pt_br": "Gerencie as strings de tradução para todos os idiomas suportados",
            "en_us": "Manage translation strings for all supported languages",
            "es_es": "Gestione las cadenas de traducción para todos los idiomas soportados",
        },
        {
            "key": "button.add",
            "namespace": "common",
            "pt_br": "Adicionar",
            "en_us": "Add",
            "es_es": "Agregar",
        },
        {
            "key": "button.edit",
            "namespace": "common",
            "pt_br": "Editar",
            "en_us": "Edit",
            "es_es": "Editar",
        },
        {
            "key": "button.delete",
            "namespace": "common",
            "pt_br": "Deletar",
            "en_us": "Delete",
            "es_es": "Eliminar",
        },
        {
            "key": "button.save",
            "namespace": "common",
            "pt_br": "Salvar",
            "en_us": "Save",
            "es_es": "Guardar",
        },
        {
            "key": "button.cancel",
            "namespace": "common",
            "pt_br": "Cancelar",
            "en_us": "Cancel",
            "es_es": "Cancelar",
        },
    ]
    
    # Load translations into in-memory database
    for trans in DEFAULT_TRANSLATIONS:
        composite_key = f"{trans['namespace']}:{trans['key']}"
        
        if composite_key not in TRANSLATIONS_DB:
            translation = TranslationSchema(
                id=composite_key,
                key=trans['key'],
                namespace=trans['namespace'],
                pt_br=trans['pt_br'],
                en_us=trans['en_us'],
                es_es=trans['es_es'],
                created_by="system",
                updated_by="system",
            )
            TRANSLATIONS_DB[composite_key] = translation
