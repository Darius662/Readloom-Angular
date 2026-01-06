#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Groq AI provider for manga metadata extraction.

Groq provides fast, free inference for LLMs.
API: https://groq.com/
Free tier: Generous rate limits, no credit card required
"""

import json
import re
from typing import Optional
from datetime import datetime

from .base import AIProvider, MangaMetadata


class GroqProvider(AIProvider):
    """Groq AI provider for metadata extraction."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq provider.
        
        Args:
            api_key: Groq API key. If not provided, will try to load from environment.
        """
        super().__init__("Groq", enabled=True, api_key=api_key)
        
        if not self.api_key:
            import os
            self.api_key = os.getenv("GROQ_API_KEY")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"  # Latest available model
        self.client = None
        
        if self.api_key:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize the Groq client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.logger.info("Groq client initialized successfully")
        except ImportError:
            self.logger.warning("groq package not installed. Install with: pip install groq")
            self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Groq provider is available.
        
        Returns:
            True if API key is set and client is initialized.
        """
        return self.api_key is not None and self.client is not None

    def extract_manga_metadata(self, manga_title: str, known_chapters: Optional[int] = None) -> Optional[MangaMetadata]:
        """Extract manga metadata using Groq.
        
        Args:
            manga_title: The title of the manga.
            known_chapters: Optional known chapter count for context.
            
        Returns:
            MangaMetadata object or None if extraction failed.
        """
        if not self.is_available():
            self.logger.warning("Groq provider is not available")
            return None

        try:
            prompt = self._build_prompt(manga_title, known_chapters)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a manga database expert. Extract accurate metadata from manga titles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent results
                max_tokens=500,
                timeout=30
            )

            response_text = response.choices[0].message.content
            metadata = self._parse_response(response_text, manga_title)
            
            if metadata:
                metadata.source = "Groq"
                metadata.raw_response = response_text
                self.logger.info(f"Groq extracted metadata for {manga_title}: {metadata.volumes} volumes, {metadata.chapters} chapters")
                return metadata
            
            return None

        except Exception as e:
            self.logger.error(f"Groq extraction failed for {manga_title}: {e}")
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
        
        return f"""Extract accurate metadata for the manga: "{manga_title}"

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
                self.logger.warning(f"No JSON found in Groq response: {response_text}")
                return None

            data = json.loads(json_match.group())

            volumes = int(data.get("volumes", 0))
            chapters = int(data.get("chapters", 0))
            status = data.get("status", "UNKNOWN").upper()
            confidence = float(data.get("confidence", 0.7))
            next_release = data.get("next_release_date")

            if volumes <= 0 or chapters <= 0:
                self.logger.warning(f"Invalid metadata from Groq: volumes={volumes}, chapters={chapters}")
                return None

            return MangaMetadata(
                title=manga_title,
                volumes=volumes,
                chapters=chapters,
                status=status,
                release_dates={},
                next_release_date=next_release,
                confidence=confidence,
                source="Groq"
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Groq JSON response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing Groq response: {e}")
            return None
