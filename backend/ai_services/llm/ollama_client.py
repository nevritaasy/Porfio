# Ollama LLM pakai model qwen2.5:1.5b, kalau unavailable akan fallback ke rule based

from __future__ import annotations

import json
import os
import re
from typing import Optional

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_MODEL = "qwen2.5:1.5b"
_GENERATE_ENDPOINT = "/api/generate"
_TIMEOUT_SECONDS = 300


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

    @staticmethod
    def _clean_summary(text: str) -> str:
        # Remove markdown bold
        text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
        # Remove header markers
        text = re.sub(r"^#{1,3}\s*", "", text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def _clean_list_output(raw: str) -> list[str]:
        # Intro/outro patterns to drop
        _FILLER_PATTERNS = re.compile(
            r"^(berikut|tentu|tentunya|baik|oke|okay|ini|mari|sebagai|selain|untuk|catatan|kesimpulan|perlu diingat)",
            re.IGNORECASE,
        )
        _OUTRO_PATTERNS = re.compile(
            r"(semoga|sekian|demikian|harapan|jadilah|terus|tetaplah)",
            re.IGNORECASE,
        )

        items: list[str] = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            # Remove markdown heading markers
            line = re.sub(r"^#{1,3}\s*", "", line)
            # Remove markdown bold
            line = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", line)
            # Strip trailing colon-headers 
            if line.endswith(":") and len(line.split()) <= 4:
                continue
            # Strip bullet/numbered prefix
            line = re.sub(r"^[-•*\d]+[.)\-]?\s*", "", line).strip()
            if not line:
                continue
            # Drop filler intro sentences
            if _FILLER_PATTERNS.match(line):
                continue
            # Drop outro sentences
            if _OUTRO_PATTERNS.search(line):
                continue
            items.append(line)
        return items

    def generate_profile_summary(self, prompt: str) -> Optional[str]:
        raw = self.generate(prompt)
        if raw is None:
            return None
        return self._clean_summary(raw) or None

    def generate_strengths(self, prompt: str) -> Optional[list[str]]:
        raw = self.generate(prompt)
        if raw is None:
            return None
        items = self._clean_list_output(raw)
        return items if items else None

    def generate_improvements(self, prompt: str) -> Optional[list[str]]:
        raw = self.generate(prompt)
        if raw is None:
            return None
        items = self._clean_list_output(raw)
        return items if items else None

    def generate_role_reason(self, prompt: str) -> Optional[str]:
        raw = self.generate(prompt)
        if raw is None:
            return None
        return self._clean_summary(raw) or None
