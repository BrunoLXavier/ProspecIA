from datetime import datetime
from app.infrastructure.models.client import Translation

class TranslationsRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self, search=None, namespace=None, limit=1000):
        query = self.session.query(Translation)
        if search:
            ilike = f"%{search}%"
            query = query.filter(
                (Translation.key.ilike(ilike)) |
                (Translation.pt_br.ilike(ilike)) |
                (Translation.en_us.ilike(ilike)) |
                (Translation.es_es.ilike(ilike))
            )
        if namespace:
            query = query.filter(Translation.namespace == namespace)
        return query.limit(limit).all()

    def create(self, key, namespace, pt_br, en_us, es_es, created_by="system"):
        translation = Translation(
            id=f"{namespace}:{key}",
            key=key,
            namespace=namespace,
            pt_br=pt_br,
            en_us=en_us,
            es_es=es_es,
            created_by=created_by,
            updated_by=created_by,
        )
        self.session.add(translation)
        self.session.commit()
        return translation

    def update(self, translation_id, pt_br=None, en_us=None, es_es=None, updated_by="system"):
        translation = self.session.query(Translation).get(translation_id)
        if not translation:
            return None
        if pt_br:
            translation.pt_br = pt_br
        if en_us:
            translation.en_us = en_us
        if es_es:
            translation.es_es = es_es
        translation.updated_by = updated_by
        translation.updated_at = datetime.utcnow()
        self.session.commit()
        return translation

    def delete(self, translation_id):
        translation = self.session.query(Translation).get(translation_id)
        if not translation:
            return False
        self.session.delete(translation)
        self.session.commit()
        return True
