"""
Ollama LLM 
If Ollama is unavailable then the result will use rule based

Configuration via environment variables:
  OLLAMA_HOST   – Ollama API base URL (default: http://localhost:11434)
  OLLAMA_MODEL  – Model to use        (default: llama3.2:3b)

Docker / remote usage:
  Set OLLAMA_HOST=http://host.docker.internal:11434 when running inside a container.
"""

from __future__ import annotations

import json
import os
from typing import Optional

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_MODEL = "llama3.2:3b"
_GENERATE_ENDPOINT = "/api/generate"
_TIMEOUT_SECONDS = 60


class OllamaClient:
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.host = (host or os.environ.get("OLLAMA_HOST") or _DEFAULT_HOST).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or _DEFAULT_MODEL
        self._available: Optional[bool] = None  

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available

        if not _REQUESTS_AVAILABLE:
            self._available = False
            return False

        try:
            resp = requests.get(self.host, timeout=3)
            self._available = resp.status_code < 500
        except Exception:
            self._available = False

        if not self._available:
            print(
                f"[ollama_client] Ollama not available at {self.host}. "
                "Falling back to rule-based explanations."
            )

        return self._available

    # Get request ke Ollama
    def generate(self, prompt: str, stream: bool = False) -> Optional[str]:
        if not self.is_available():
            return None

        url = self.host + _GENERATE_ENDPOINT
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
        }

        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT_SECONDS)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip() or None
        except Exception as exc:
            print(f"[ollama_client] generate() failed: {exc}")
            return None

    # Helper 
    def generate_profile_summary(self, prompt: str) -> Optional[str]:
        return self.generate(prompt)

    def generate_strengths(self, prompt: str) -> Optional[list[str]]:
        raw = self.generate(prompt)
        if raw is None:
            return None
        lines = [
            line.lstrip("-•*123456789. ").strip()
            for line in raw.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        return [ln for ln in lines if ln] or None

    def generate_improvements(self, prompt: str) -> Optional[list[str]]:
        return self.generate_strengths(prompt)  

    def generate_role_reason(self, prompt: str) -> Optional[str]:
        return self.generate(prompt)
