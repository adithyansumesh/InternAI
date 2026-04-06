"""
services/nlp_service.py — spaCy NLP service.
Provides named entity recognition, noun chunk extraction, and
linguistic analysis used by the resume parser and matching engine.
"""

import re
from typing import List, Dict, Tuple, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


class NLPService:
    """Wraps spaCy model for NLP tasks across the application."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self._nlp = None
        self._load_model()

    def _load_model(self):
        try:
            import spacy
            self._nlp = spacy.load(self.model_name)
            logger.info(f"spaCy model '{self.model_name}' loaded successfully")
        except OSError:
            logger.warning(f"spaCy model '{self.model_name}' not found. Run: python -m spacy download {self.model_name}")
            self._nlp = None
        except ImportError:
            logger.warning("spaCy not installed. NLP features will be limited.")
            self._nlp = None

    @property
    def nlp(self):
        return self._nlp

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities grouped by label.
        Returns dict like: {"PERSON": ["John Doe"], "ORG": ["Google"], ...}
        """
        if not self._nlp:
            return {}

        doc = self._nlp(text[:100000])  # spaCy max length guard
        entities: Dict[str, List[str]] = {}

        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            if ent.text not in entities[label]:
                entities[label].append(ent.text.strip())

        return entities

    def extract_noun_chunks(self, text: str) -> List[str]:
        """Extract meaningful noun phrases from text."""
        if not self._nlp:
            return []
        doc = self._nlp(text[:50000])
        return [chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 2]

    def extract_email(self, text: str) -> Optional[str]:
        """Extract first email address found in text."""
        pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract first phone number found in text."""
        pattern = r"(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?)(\d{3}[\s\-]?\d{4})"
        match = re.search(pattern, text)
        return match.group(0).strip() if match else None

    def extract_name(self, text: str) -> Optional[str]:
        """
        Attempt to extract candidate name from top of resume.
        Looks for PERSON entities; falls back to first capitalized line.
        """
        entities = self.extract_entities(text[:500])
        persons = entities.get("PERSON", [])
        if persons:
            return persons[0]

        # Fallback: first non-empty line that looks like a name
        for line in text.split("\n")[:5]:
            line = line.strip()
            if line and len(line.split()) in (2, 3) and line.istitle():
                return line

        return None

    def tokenize_keywords(self, text: str) -> List[str]:
        """
        Extract significant keyword tokens (nouns, proper nouns, adjectives).
        Useful for skill extraction fallback.
        """
        if not self._nlp:
            return text.lower().split()

        doc = self._nlp(text.lower()[:50000])
        return [
            token.lemma_
            for token in doc
            if token.pos_ in ("NOUN", "PROPN", "ADJ")
            and not token.is_stop
            and not token.is_punct
            and len(token.text) > 2
        ]
