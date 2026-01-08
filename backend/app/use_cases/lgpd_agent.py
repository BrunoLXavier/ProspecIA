"""
LGPD Agent for PII Detection and Data Masking.

Implements:
- PII detection using BERTimbau (Brazilian Portuguese)
- Data masking with reversible tokenization
- Consent validation
- Kafka audit logging
"""

import re
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

from app.domain.repositories.consentimento_repository import ConsentimentoRepository
from app.adapters.kafka.producer import get_kafka_producer


logger = structlog.get_logger(__name__)


class LGPDAgent:
    """
    LGPD compliance agent for PII detection, masking, and consent validation.
    
    Uses BERTimbau model for Brazilian Portuguese NER (Named Entity Recognition).
    Detects CPF, CNPJ, RG, email, phone numbers, and other PII.
    """
    
    def __init__(self, model_path: str = "neuralmind/bert-base-portuguese-cased"):
        """
        Initialize LGPD Agent with BERTimbau model.
        
        Args:
            model_path: Path to BERTimbau model (local or HuggingFace)
        """
        self.model_path = model_path
        self.ner_pipeline = None
        self.tokenizer = None
        self.model = None
        self._load_model()
        
        # Regex patterns for Brazilian documents and PII
        self.cpf_pattern = re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b')
        self.cnpj_pattern = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b')
        self.rg_pattern = re.compile(r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b')
        self.pis_pattern = re.compile(r'\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b')  # PIS/PASEP pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b')
        # Date of birth pattern (DD/MM/YYYY or DD-MM-YYYY)
        self.birthdate_pattern = re.compile(r'\b(?:0[1-9]|[12]\d|3[01])[-/](?:0[1-9]|1[0-2])[-/](?:19|20)\d{2}\b')
        # Brazilian address pattern (generic)
        self.address_pattern = re.compile(r'\b(?:Rua|Avenida|Av\.|Travessa|Trav\.|Praça|Pça\.)\s+[A-Za-záéíóúãõç\s]+,?\s*\d+(?:\s*[-,]\s*(?:Apto|Apt\.|Bloco|Blco\.)\s*\d+)?')
        # Biometric pattern (fingerprint references)
        self.biometric_pattern = re.compile(r'(?:impressão|impressão digital|biometria|digital|fingerprint)[\s:]*[\w\d]+', re.IGNORECASE)
        
        logger.info("lgpd_agent_initialized", model_path=model_path)
    
    def _load_model(self):
        """Load BERTimbau model for NER."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_path)
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                device=device,
                aggregation_strategy="simple"
            )
            logger.info("bertimbau_model_loaded", device="cuda" if device == 0 else "cpu")
        except Exception as e:
            logger.error("model_loading_failed", error=str(e))
            raise
    
    def detect_pii(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect PII in text using BERTimbau NER and regex patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with PII types and detected entities:
            {
                "cpf": [{"value": "123.456.789-00", "start": 10, "end": 24}],
                "cnpj": [...],
                "rg": [...],
                "pis": [...],
                "email": [...],
                "phone": [...],
                "birthdate": [...],
                "address": [...],
                "biometric": [...],
                "person": [...],  # From NER
                "location": [...]  # From NER
            }
        """
        pii_detected = {
            "cpf": [],
            "cnpj": [],
            "rg": [],
            "pis": [],
            "email": [],
            "phone": [],
            "birthdate": [],
            "address": [],
            "biometric": [],
            "person": [],
            "location": [],
            "organization": []
        }
        
        # Regex-based detection for Brazilian documents
        for match in self.cpf_pattern.finditer(text):
            pii_detected["cpf"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.cnpj_pattern.finditer(text):
            pii_detected["cnpj"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.rg_pattern.finditer(text):
            pii_detected["rg"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.pis_pattern.finditer(text):
            pii_detected["pis"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.email_pattern.finditer(text):
            pii_detected["email"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.phone_pattern.finditer(text):
            pii_detected["phone"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.birthdate_pattern.finditer(text):
            pii_detected["birthdate"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.address_pattern.finditer(text):
            pii_detected["address"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        for match in self.biometric_pattern.finditer(text):
            pii_detected["biometric"].append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0
            })
        
        # NER-based detection for names, locations, organizations
        try:
            ner_results = self.ner_pipeline(text[:5000])  # Limit to 5000 chars for performance
            
            for entity in ner_results:
                entity_type = entity.get("entity_group", "").lower()
                
                if "per" in entity_type or "person" in entity_type:
                    pii_detected["person"].append({
                        "value": entity["word"],
                        "start": entity["start"],
                        "end": entity["end"],
                        "confidence": entity["score"]
                    })
                elif "loc" in entity_type or "location" in entity_type:
                    pii_detected["location"].append({
                        "value": entity["word"],
                        "start": entity["start"],
                        "end": entity["end"],
                        "confidence": entity["score"]
                    })
                elif "org" in entity_type or "organization" in entity_type:
                    pii_detected["organization"].append({
                        "value": entity["word"],
                        "start": entity["start"],
                        "end": entity["end"],
                        "confidence": entity["score"]
                    })
        
        except Exception as e:
            logger.error("ner_detection_failed", error=str(e))
        
        # Log summary
        total_pii = sum(len(v) for v in pii_detected.values())
        logger.info("pii_detection_complete", total_entities=total_pii, by_type={k: len(v) for k, v in pii_detected.items()})
        
        return pii_detected
    
    def mask_pii(self, text: str, pii_detected: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Mask PII with reversible tokens.
        
        Args:
            text: Original text
            pii_detected: PII entities from detect_pii()
            
        Returns:
            {
                "masked_text": "Text with [CPF_TOKEN_uuid] replacements",
                "tokens": {
                    "CPF_TOKEN_abc123": "123.456.789-00",
                    "EMAIL_TOKEN_def456": "user@example.com"
                },
                "actions_taken": ["masked_5_cpf", "masked_2_email"]
            }
        """
        masked_text = text
        tokens = {}
        actions_taken = []
        
        # Sort entities by start position (reverse) to preserve offsets
        all_entities = []
        for pii_type, entities in pii_detected.items():
            for entity in entities:
                all_entities.append({
                    "type": pii_type,
                    "value": entity["value"],
                    "start": entity["start"],
                    "end": entity["end"]
                })
        
        all_entities.sort(key=lambda x: x["start"], reverse=True)
        
        # Replace entities with tokens
        for entity in all_entities:
            token_id = str(uuid.uuid4())[:8]
            token_name = f"{entity['type'].upper()}_TOKEN_{token_id}"
            
            masked_text = (
                masked_text[:entity["start"]] +
                f"[{token_name}]" +
                masked_text[entity["end"]:]
            )
            
            tokens[token_name] = entity["value"]
        
        # Count actions
        for pii_type in pii_detected:
            count = len(pii_detected[pii_type])
            if count > 0:
                actions_taken.append(f"masked_{count}_{pii_type}")
        
        logger.info("pii_masking_complete", total_tokens=len(tokens), actions=actions_taken)
        
        return {
            "masked_text": masked_text,
            "tokens": tokens,
            "actions_taken": actions_taken
        }
    
    async def validate_consent(
        self,
        consentimento_id: Optional[uuid.UUID],
        titular_id: Optional[uuid.UUID],
        finalidade: str,
        repository: ConsentimentoRepository
    ) -> Dict[str, Any]:
        """
        Validate LGPD consent for data processing.
        
        Args:
            consentimento_id: Consent UUID
            titular_id: Data subject UUID
            finalidade: Data processing purpose
            repository: Consent repository
            
        Returns:
            {
                "valid": bool,
                "consent": Consentimento or None,
                "reason": str
            }
        """
        if not consentimento_id:
            logger.warning("consent_validation_failed", reason="no_consent_id_provided")
            return {
                "valid": False,
                "consent": None,
                "reason": "Nenhum consentimento informado"
            }
        
        try:
            consent = await repository.get_by_id(consentimento_id)
            
            if not consent:
                return {
                    "valid": False,
                    "consent": None,
                    "reason": "Consentimento não encontrado"
                }
            
            if not consent.is_valido():
                return {
                    "valid": False,
                    "consent": consent,
                    "reason": "Consentimento revogado ou expirado"
                }
            
            logger.info("consent_validation_success", consentimento_id=str(consentimento_id))
            return {
                "valid": True,
                "consent": consent,
                "reason": "Consentimento válido"
            }
        
        except Exception as e:
            logger.error("consent_validation_error", error=str(e))
            return {
                "valid": False,
                "consent": None,
                "reason": f"Erro ao validar consentimento: {str(e)}"
            }
    
    async def process_ingestao(
        self,
        text_content: str,
        consentimento_id: Optional[uuid.UUID],
        titular_id: Optional[uuid.UUID],
        finalidade: str,
        ingestao_id: uuid.UUID,
        repository: ConsentimentoRepository
    ) -> Dict[str, Any]:
        """
        Full LGPD processing pipeline: detect → mask → validate → log.
        
        Args:
            text_content: Text to process
            consentimento_id: Consent UUID
            titular_id: Data subject UUID
            finalidade: Processing purpose
            ingestao_id: Ingestion record UUID
            repository: Consent repository
            
        Returns:
            {
                "pii_detected": {...},
                "masked_data": {...},
                "consent_validation": {...},
                "compliance_score": int (0-100)
            }
        """
        logger.info("lgpd_processing_started", ingestao_id=str(ingestao_id))
        
        # Step 1: Detect PII
        pii_detected = self.detect_pii(text_content)
        
        # Step 2: Mask PII
        masked_data = self.mask_pii(text_content, pii_detected)
        
        # Step 3: Validate consent
        consent_validation = await self.validate_consent(
            consentimento_id,
            titular_id,
            finalidade,
            repository
        )
        
        # Step 4: Calculate compliance score
        compliance_score = self._calculate_compliance_score(pii_detected, consent_validation)
        
        # Step 5: Log to Kafka
        kafka_producer = get_kafka_producer()
        if kafka_producer:
            try:
                kafka_producer.publish_lgpd_decision(
                    ingestao_id=str(ingestao_id),
                    pii_detectado=pii_detected,
                    acoes_tomadas=masked_data["actions_taken"],
                    consentimento_validado=bool(consent_validation["valid"]),
                    score_confiabilidade=compliance_score,
                )
            except Exception as e:
                logger.error("kafka_logging_failed", error=str(e))
        
        logger.info("lgpd_processing_complete", ingestao_id=str(ingestao_id), compliance_score=compliance_score)
        
        return {
            "pii_detected": pii_detected,
            "masked_data": masked_data,
            "consent_validation": consent_validation,
            "compliance_score": compliance_score
        }
    
    def _calculate_compliance_score(
        self,
        pii_detected: Dict[str, List[Dict[str, Any]]],
        consent_validation: Dict[str, Any]
    ) -> int:
        """
        Calculate LGPD compliance score (0-100).
        
        Factors:
        - PII detection coverage: 30 points
        - Consent validation: 40 points
        - Data minimization: 30 points
        """
        score = 0
        
        # PII detection coverage (30 points)
        total_pii = sum(len(v) for v in pii_detected.values())
        if total_pii > 0:
            score += 30
        
        # Consent validation (40 points)
        if consent_validation["valid"]:
            score += 40
        elif consent_validation["consent"] is not None:
            score += 20  # Partial credit for attempting consent
        
        # Data minimization (30 points)
        # Fewer PII types = better score
        pii_types_found = sum(1 for v in pii_detected.values() if v)
        if pii_types_found <= 2:
            score += 30
        elif pii_types_found <= 4:
            score += 20
        elif pii_types_found <= 6:
            score += 10
        
        return min(score, 100)


# Global instance
_lgpd_agent: Optional[LGPDAgent] = None


def get_lgpd_agent() -> LGPDAgent:
    """Get global LGPD agent instance."""
    global _lgpd_agent
    if _lgpd_agent is None:
        _lgpd_agent = LGPDAgent()
    return _lgpd_agent
