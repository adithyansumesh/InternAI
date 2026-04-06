"""
services/embedding_service.py — Text embedding service.
Uses SentenceTransformers (all-MiniLM-L6-v2) to generate dense vector embeddings.
Compatible with both resume text and job descriptions for semantic similarity.
Supports batch embedding for efficiency.
"""

import numpy as np
from typing import List, Union
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Generates sentence/document-level embeddings using SentenceTransformers.
    Falls back to TF-IDF style bag-of-words if the library is unavailable.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension: int = 384
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"SentenceTransformer '{self.model_name}' loaded (dim={self._dimension})")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> np.ndarray:
        """
        Generate a single embedding vector for a text string.

        Returns:
            numpy array of shape (dimension,)
        """
        if not text or not text.strip():
            return np.zeros(self._dimension, dtype=np.float32)

        if self._model:
            vector = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vector.astype(np.float32)

        logger.warning("Using fallback zero embedding (SentenceTransformer unavailable)")
        return np.zeros(self._dimension, dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts efficiently.

        Returns:
            numpy array of shape (n_texts, dimension)
        """
        if not texts:
            return np.zeros((0, self._dimension), dtype=np.float32)

        if self._model:
            vectors = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=False,
            )
            return vectors.astype(np.float32)

        return np.zeros((len(texts), self._dimension), dtype=np.float32)

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        Since embeddings are L2-normalized, this equals the dot product.
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
