#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ollama AI provider for manga metadata extraction.

Ollama provides self-hosted LLM inference without external dependencies.
Installation: https://ollama.ai/
Models: Llama 3.3, Mistral, and many others
Free: Completely free, runs locally
"""

import json
import re
from typing import Optional
import requests

from .base import AIProvider, MangaMetadata


class OllamaProvider(AIProvider):
    """Ollama AI provider for metadata extraction (self-hosted)."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize Ollama provider.
        
        Args:
            base_url: Ollama server URL. Defaults to http://localhost:11434
            model: Model to use. Defaults to llama2. Can also be set via OLLAMA_MODEL env var.
        """
        super().__init__("Ollama", enabled=True)
        
        import os
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = 60  # Ollama can be slow on first run
        
        # Don't require API key for Ollama (it's self-hosted)
        self.api_key = "local"

    def is_available(self) -> bool:
        """Check if Ollama provider is available.
        
        Returns:
            True if Ollama server is reachable.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                self.logger.debug("Ollama server is reachable")
                return True
            else:
                self.logger.warning(f"Ollama server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.logger.debug(f"Ollama server not reachable at {self.base_url}")
            return False
        except Exception as e:
            self.logger.warning(f"Error checking Ollama availability: {e}")
            return False

    def extract_manga_metadata(self, manga_title: str, known_chapters: Optional[int] = None) -> Optional[MangaMetadata]:
        """Extract manga metadata using Ollama.
        
        Args:
            manga_title: The title of the manga.
            known_chapters: Optional known chapter count for context.
            
        Returns:
            MangaMetadata object or None if extraction failed.
        """
        if not self.is_available():
            self.logger.warning("Ollama provider is not available")
            return None

        try:
            prompt = self._build_prompt(manga_title, known_chapters)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return None

            response_data = response.json()
            response_text = response_data.get("response", "")
            
            metadata = self._parse_response(response_text, manga_title)
            
            if metadata:
                metadata.source = "Ollama"
                metadata.raw_response = response_text
                self.logger.info(f"Ollama extracted metadata for {manga_title}: {metadata.volumes} volumes, {metadata.chapters} chapters")
                return metadata
            
            return None

        except requests.exceptions.Timeout:
            self.logger.error(f"Ollama request timed out for {manga_title}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Cannot connect to Ollama server at {self.base_url}")
            return None
        except Exception as e:
            self.logger.error(f"Ollama extraction failed for {manga_title}: {e}")
            return None

    def _build_prompt(self, manga_title: str, known_chapters: Optional[int] = None) -> str:
        """Build the prompt for metadata extraction.
        
        Args:
            manga_title: The manga title.
            known_chapters: Optional known chapter count.
            
        Returns:
            The prompt string.
        """
        context = f"Known chapters: {known_chapters}" if known_chapters else "No chapter info available"
        
        return f"""You are a manga database expert. Extract accurate metadata for the manga: "{manga_title}"

{context}

Please provide the following information in JSON format:
{{
    "volumes": <number of volumes or best estimate>,
    "chapters": <total number of chapters or best estimate>,
    "status": "<ONGOING, COMPLETED, HIATUS, or CANCELLED>",
    "next_release_date": "<YYYY-MM-DD or null if unknown>",
    "confidence": <0.0-1.0 confidence score>,
    "notes": "<any relevant notes>"
}}

Return ONLY valid JSON, no additional text."""

    def _parse_response(self, response_text: str, manga_title: str) -> Optional[MangaMetadata]:
        """Parse the AI response into MangaMetadata.
        
        Args:
            response_text: The response from the AI.
            manga_title: The original manga title.
            
        Returns:
            MangaMetadata object or None if parsing failed.
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                self.logger.warning(f"No JSON found in Ollama response: {response_text}")
                return None

            data = json.loads(json_match.group())

            volumes = int(data.get("volumes", 0))
            chapters = int(data.get("chapters", 0))
            status = data.get("status", "UNKNOWN").upper()
            confidence = float(data.get("confidence", 0.7))
            next_release = data.get("next_release_date")

            if volumes <= 0 or chapters <= 0:
                self.logger.warning(f"Invalid metadata from Ollama: volumes={volumes}, chapters={chapters}")
                return None

            return MangaMetadata(
                title=manga_title,
                volumes=volumes,
                chapters=chapters,
                status=status,
                release_dates={},
                next_release_date=next_release,
                confidence=confidence,
                source="Ollama"
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Ollama JSON response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing Ollama response: {e}")
            return None
