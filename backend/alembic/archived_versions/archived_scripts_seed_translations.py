#!/usr/bin/env python3
"""
Seed script to populate initial translations in the database.
"""
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text

def seed_translations():
    """Seed initial translations for the system."""
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql://prospecai_user:prospecai_password@postgres:5432/prospecai')
    
    # Create synchronous engine
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if translations table exists
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'translations')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ Table 'translations' does not exist. Please run migrations first.")
                return False
            
            # Clear existing translations (optional - comment out if you want to keep existing)
            conn.execute(text("DELETE FROM translations"))
            conn.commit()
            print("🧹 Cleared existing translations")
        
        # Common translations
        common_translations = [
            {
                "id": "common:app_title",
                "key": "app_title",
                "namespace": "common",
                "pt_br": "ProspecIA",
                "en_us": "ProspecIA",
                "es_es": "ProspecIA",
            },
            {
                "id": "common:app_subtitle",
                "key": "app_subtitle",
                "namespace": "common",
                "pt_br": "Sistema de Gestão de Inovação",
                "en_us": "Innovation Management System",
                "es_es": "Sistema de Gestión de Innovación",
            },
            {
                "id": "common:save",
                "key": "save",
                "namespace": "common",
                "pt_br": "Salvar",
                "en_us": "Save",
                "es_es": "Guardar",
            },
            {
                "id": "common:cancel",
                "key": "cancel",
                "namespace": "common",
                "pt_br": "Cancelar",
                "en_us": "Cancel",
                "es_es": "Cancelar",
            },
            {
                "id": "common:delete",
                "key": "delete",
                "namespace": "common",
                "pt_br": "Excluir",
                "en_us": "Delete",
                "es_es": "Eliminar",
            },
            {
                "id": "common:edit",
                "key": "edit",
                "namespace": "common",
                "pt_br": "Editar",
                "en_us": "Edit",
                "es_es": "Editar",
            },
        ]
        
        # Admin translations
        admin_translations = [
            {
                "id": "admin:translations_title",
                "key": "translations_title",
                "namespace": "admin",
                "pt_br": "Gerenciamento de Traduções",
                "en_us": "Translation Management",
                "es_es": "Gestión de Traducciones",
            },
            {
                "id": "admin:translations_description",
                "key": "translations_description",
                "namespace": "admin",
                "pt_br": "Configure as traduções do sistema",
                "en_us": "Configure system translations",
                "es_es": "Configure las traducciones del sistema",
            },
            {
                "id": "admin:key",
                "key": "key",
                "namespace": "admin",
                "pt_br": "Chave",
                "en_us": "Key",
                "es_es": "Clave",
            },
            {
                "id": "admin:namespace",
                "key": "namespace",
                "namespace": "admin",
                "pt_br": "Namespace",
                "en_us": "Namespace",
                "es_es": "Espacio de nombres",
            },
            {
                "id": "admin:portuguese",
                "key": "portuguese",
                "namespace": "admin",
                "pt_br": "Português",
                "en_us": "Portuguese",
                "es_es": "Portugués",
            },
            {
                "id": "admin:english",
                "key": "english",
                "namespace": "admin",
                "pt_br": "Inglês",
                "en_us": "English",
                "es_es": "Inglés",
            },
            {
                "id": "admin:spanish",
                "key": "spanish",
                "namespace": "admin",
                "pt_br": "Espanhol",
                "en_us": "Spanish",
                "es_es": "Español",
            },
        ]
        
        # Ingestion translations
        ingestion_translations = [
            {
                "id": "ingestion:title",
                "key": "title",
                "namespace": "ingestion",
                "pt_br": "Ingestão de Dados",
                "en_us": "Data Ingestion",
                "es_es": "Ingestión de Datos",
            },
            {
                "id": "ingestion:source",
                "key": "source",
                "namespace": "ingestion",
                "pt_br": "Fonte",
                "en_us": "Source",
                "es_es": "Fuente",
            },
            {
                "id": "ingestion:status",
                "key": "status",
                "namespace": "ingestion",
                "pt_br": "Status",
                "en_us": "Status",
                "es_es": "Estado",
            },
        ]
        
        # Wave2 translations
        wave2_translations = [
            {
                "id": "wave2:funding_sources",
                "key": "funding_sources",
                "namespace": "wave2",
                "pt_br": "Fontes de Fomento",
                "en_us": "Funding Sources",
                "es_es": "Fuentes de Financiamiento",
            },
            {
                "id": "wave2:clients",
                "key": "clients",
                "namespace": "wave2",
                "pt_br": "Clientes",
                "en_us": "Clients",
                "es_es": "Clientes",
            },
            {
                "id": "wave2:opportunities",
                "key": "opportunities",
                "namespace": "wave2",
                "pt_br": "Oportunidades",
                "en_us": "Opportunities",
                "es_es": "Oportunidades",
            },
            {
                "id": "wave2:portfolio",
                "key": "portfolio",
                "namespace": "wave2",
                "pt_br": "Portfólio",
                "en_us": "Portfolio",
                "es_es": "Portafolio",
            },
        ]
        
        # Combine all translations
        all_translations = (
            common_translations +
            admin_translations +
            ingestion_translations +
            wave2_translations
        )
        
        # Insert translations using raw SQL
        insert_sql = text("""
            INSERT INTO translations (id, key, namespace, pt_br, en_us, es_es, created_at, updated_at, created_by, updated_by)
            VALUES (:id, :key, :namespace, :pt_br, :en_us, :es_es, :created_at, :updated_at, :created_by, :updated_by)
        """)
        
        now = datetime.utcnow()
        for trans_data in all_translations:
            trans_data['created_at'] = now
            trans_data['updated_at'] = now
            trans_data['created_by'] = 'system'
            trans_data['updated_by'] = 'system'
            conn.execute(insert_sql, trans_data)
        
        conn.commit()
        print(f"✅ Successfully seeded {len(all_translations)} translations")
        
        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM translations"))
        count = result.scalar()
        print(f"📊 Total translations in database: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding translations: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = seed_translations()
    sys.exit(0 if success else 1)
