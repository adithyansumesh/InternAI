"""
services/llm_service.py — LLM API service (OpenAI-compatible).
Provides a clean interface for text generation using OpenAI (or compatible) APIs.
Supports chat completions with configurable models, temperature, and system prompts.
"""

from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Wrapper for OpenAI-compatible LLM API.
    Compatible with: OpenAI, Azure OpenAI, Groq, Together.ai, Ollama (local).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            logger.info(f"LLM client initialized: model='{self.model}', base_url='{self.base_url}'")
        except ImportError:
            logger.warning("openai SDK not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"LLM client initialization failed: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """
        Generate text from the LLM.

        Args:
            prompt: User-facing prompt / instruction.
            system_prompt: Optional system message to set context/persona.
            temperature: Creativity (0.0 = deterministic, 1.0 = creative).
            max_tokens: Maximum tokens in the response.

        Returns:
            Generated text string.

        Raises:
            RuntimeError: If the LLM client is not available.
        """
        if not self._client:
            raise RuntimeError(
                "LLM client is not initialized. "
                "Ensure OPENAI_API_KEY is set and openai SDK is installed."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.debug(f"LLM request: model={self.model}, tokens<={max_tokens}")

        try:
            print(f"DEBUG: Calling LLM ({self.model})...")
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            print("DEBUG: LLM responded successfully!")
            content = response.choices[0].message.content.strip()
            logger.info(f"LLM response received: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise RuntimeError(f"LLM generation error: {str(e)}")

    def is_available(self) -> bool:
        return self._client is not None
