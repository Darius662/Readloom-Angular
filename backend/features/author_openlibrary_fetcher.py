#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author fetcher from OpenLibrary API.

Fetches author information including biography, birth date, and photos.
"""

import requests
import json
from typing import Optional, Dict, Any
from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def fetch_author_from_openlibrary(author_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch author information from OpenLibrary.
    
    Args:
        author_name: Author name to search for
    
    Returns:
        dict: Author data (biography, birth_date, photo_url, etc.) or None
    """
    try:
        # Search for author on OpenLibrary
        search_url = "https://openlibrary.org/search/authors.json"
        params = {
            "q": author_name,
            "limit": 1
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("docs") or len(data["docs"]) == 0:
            LOGGER.debug(f"No author found on OpenLibrary for: {author_name}")
            return None
        
        author = data["docs"][0]
        
        # Extract author information
        author_data = {
            "name": author.get("name"),
            "biography": author.get("bio"),
            "birth_date": author.get("birth_date"),
            "death_date": author.get("death_date"),
            "photo_url": None,
            "openlibrary_key": author.get("key"),
            "work_count": author.get("work_count", 0)
        }
        
        # Try to get author photo
        if author.get("has_photos") and author.get("photos"):
            photo_id = author["photos"][0]
            author_data["photo_url"] = f"https://covers.openlibrary.org/a/id/{photo_id}-M.jpg"
        
        # Try to get book cover as fallback
        if not author_data["photo_url"] and author.get("top_work"):
            top_work = author.get("top_work")
            if top_work:
                work_key = top_work.replace("/works/", "")
                author_data["photo_url"] = f"https://covers.openlibrary.org/w/id/{work_key}-M.jpg"
        
        LOGGER.info(f"Found author on OpenLibrary: {author_name}")
        return author_data
    
    except requests.Timeout:
        LOGGER.debug(f"Timeout fetching author from OpenLibrary: {author_name}")
        return None
    except Exception as e:
        LOGGER.debug(f"Error fetching author from OpenLibrary: {e}")
        return None


def update_author_from_openlibrary(author_id: int, author_name: str) -> bool:
    """
    Fetch and update author from OpenLibrary.
    
    Args:
        author_id: Author ID
        author_name: Author name
    
    Returns:
        bool: True if author was updated
    """
    try:
        LOGGER.info(f"Fetching author data from OpenLibrary: {author_name}")
        
        # Fetch author data
        author_data = fetch_author_from_openlibrary(author_name)
        
        if not author_data:
            LOGGER.debug(f"Could not fetch author data from OpenLibrary: {author_name}")
            return False
        
        # Build update query
        updates = []
        params = []
        
        if author_data.get("biography"):
            updates.append("biography = ?")
            params.append(author_data["biography"])
        
        if author_data.get("birth_date"):
            updates.append("birth_date = ?")
            params.append(author_data["birth_date"])
        
        # Try to update photo_url if column exists
        if author_data.get("photo_url"):
            try:
                updates.append("photo_url = ?")
                params.append(author_data["photo_url"])
            except Exception as e:
                LOGGER.debug(f"Could not add photo_url to update: {e}")
        
        if not updates:
            LOGGER.debug(f"No data to update for author: {author_name}")
            return False
        
        # Add updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(author_id)
        
        # Execute update
        query = f"""
            UPDATE authors 
            SET {', '.join(updates)}
            WHERE id = ?
        """
        
        try:
            execute_query(query, params, commit=True)
        except Exception as e:
            # If photo_url column doesn't exist, try without it
            if "photo_url" in str(e):
                LOGGER.debug(f"photo_url column doesn't exist, updating without it: {e}")
                # Rebuild query without photo_url
                updates = []
                params = []
                
                if author_data.get("biography"):
                    updates.append("biography = ?")
                    params.append(author_data["biography"])
                
                if author_data.get("birth_date"):
                    updates.append("birth_date = ?")
                    params.append(author_data["birth_date"])
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(author_id)
                    
                    query = f"""
                        UPDATE authors 
                        SET {', '.join(updates)}
                        WHERE id = ?
                    """
                    execute_query(query, params, commit=True)
            else:
                raise
        
        LOGGER.info(f"Updated author {author_name} from OpenLibrary")
        return True
    
    except Exception as e:
        LOGGER.error(f"Error updating author from OpenLibrary: {e}")
        return False


def get_book_cover_from_openlibrary(book_title: str, author_name: str) -> Optional[str]:
    """
    Get book cover from OpenLibrary by searching for "{book_title} {author_name}".
    
    Args:
        book_title: The book title to search for
        author_name: The author name to include in search
    
    Returns:
        str: Cover URL or None if not found
    """
    try:
        # Build search query
        search_query = f"{book_title} {author_name}"
        LOGGER.info(f"Searching for cover: {search_query}")
        
        # Search OpenLibrary
        search_url = "https://openlibrary.org/search.json"
        params = {
            "q": search_query,
            "limit": 1,  # Only need the first result
            "fields": "cover_i,title,author_name,key"  # Only get needed fields
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("docs") and len(data["docs"]) > 0:
            doc = data["docs"][0]
            
            # Check if cover exists
            if doc.get("cover_i"):
                cover_id = doc["cover_i"]
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                LOGGER.info(f"Found cover ID {cover_id} for {search_query}")
                return cover_url
            else:
                LOGGER.debug(f"No cover found for {search_query} in first result")
                return None
        else:
            LOGGER.debug(f"No search results for {search_query}")
            return None
    
    except requests.Timeout:
        LOGGER.debug(f"Timeout searching for cover: {search_query}")
        return None
    except requests.RequestException as e:
        LOGGER.debug(f"Network error searching for cover: {e}")
        return None
    except Exception as e:
        LOGGER.error(f"Error searching for cover: {e}")
        return None


def get_author_popular_books_ai(author_id: int, author_name: str) -> list:
    """
    Get popular books for an author using AI (Groq).
    
    Args:
        author_id: Author ID (for caching/logging)
        author_name: Author name to search for
    
    Returns:
        list: List of popular books with covers and metadata
    """
    try:
        LOGGER.info(f"Fetching popular books from AI: {author_name}")
        
        # Import Groq client
        try:
            from groq import Groq
            import os
            client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        except ImportError:
            LOGGER.error("Groq library not installed or API key not found")
            return []
        except Exception as e:
            LOGGER.error(f"Error initializing Groq client: {e}")
            return []
        
        # Ask AI for popular books
        prompt = f"""You are a book expert specializing in {author_name}'s bibliography. 
List the top 5 most popular books specifically written by {author_name}.

CRITICAL RULES:
- ONLY list books actually written by {author_name}
- Do NOT list books by other authors
- List 5 Books
- List only book titles nothing else"""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Use current supported model
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=300
            )
            
            response = completion.choices[0].message.content
            LOGGER.info(f"AI response for {author_name}: {response}")
            
            # Parse the AI response
            popular_books = []
            lines = response.strip().split('\n')
            
            # Keywords that indicate apology/explanation text (skip these)
            skip_keywords = [
                "i couldn't", "i'm not", "i don't", "i am", "however", "if you", 
                "it's possible", "can you", "would you", "please", "sorry",
                "unknown", "not found", "no information", "lesser-known", "emerging"
            ]
            
            for i, line in enumerate(lines[:5]):  # Take up to 5 books
                # Clean up the line (remove numbering, bullets, etc.)
                book_title = line.strip()
                
                # Remove common prefixes
                prefixes_to_remove = ['1. ', '2. ', '3. ', '4. ', '5. ', '• ', '- ', '* ', '1)', '2)', '3)', '4)', '5)']
                for prefix in prefixes_to_remove:
                    if book_title.startswith(prefix):
                        book_title = book_title[len(prefix):].strip()
                        break
                
                # Remove quotes and extra formatting
                book_title = book_title.strip('"').strip('*').strip()
                
                # Validate: skip if it's apology/explanation text
                if book_title and len(book_title) > 2:
                    line_lower = book_title.lower()
                    is_apology_text = any(keyword in line_lower for keyword in skip_keywords)
                    
                    if not is_apology_text:
                        # Additional validation: should look like a book title
                        if (book_title.count(' ') >= 1 or len(book_title) > 10) and len(book_title) < 100:
                            # Create book object
                            book = {
                                "id": f"ai_{author_id}_{i}",
                                "title": book_title,
                                "cover_url": None,
                                "author": author_name,
                                "source": "ai_generated"
                            }
                            
                            popular_books.append(book)
                            LOGGER.info(f"Added AI popular book: {book_title}")
                        else:
                            LOGGER.debug(f"Skipped invalid book title format: {book_title}")
                    else:
                        LOGGER.debug(f"Skipped apology text: {book_title}")
                else:
                    LOGGER.debug(f"Skipped empty/short line: {book_title}")
            
            LOGGER.info(f"Found {len(popular_books)} popular books for {author_name} via AI")
            return popular_books
            
        except Exception as e:
            LOGGER.error(f"Error calling Groq API: {e}")
            return []
    
    except Exception as e:
        LOGGER.error(f"Error in get_author_popular_books_ai: {e}")
        return []


def get_author_popular_books(author_id: int, author_name: str) -> list:
    """
    Get popular books for an author using OpenLibrary (primary) and AI (fallback).
    
    Priority:
    1. OpenLibrary - More reliable for actual author works
    2. AI (Groq) - Fallback for authors not on OpenLibrary
    
    Args:
        author_id: Author ID (for caching/logging)
        author_name: Author name to search for
    
    Returns:
        list: List of popular books with covers and metadata
    """
    # Priority 1: Try OpenLibrary first (more reliable for actual author works)
    popular_books = get_author_popular_books_openlibrary(author_id, author_name)
    
    if popular_books:
        LOGGER.info(f"Successfully got {len(popular_books)} popular books from OpenLibrary for {author_name}")
        return popular_books
    
    # Priority 2: Fallback to AI if OpenLibrary fails
    LOGGER.info(f"OpenLibrary failed, trying AI fallback for {author_name}")
    return get_author_popular_books_ai(author_id, author_name)


def get_author_popular_books_openlibrary(author_id: int, author_name: str) -> list:
    """
    Get popular books for an author from OpenLibrary (fallback method).
    
    Args:
        author_id: Author ID (for caching/logging)
        author_name: Author name to search for
    
    Returns:
        list: List of popular books with covers and metadata
    """
    try:
        LOGGER.info(f"Fetching popular books from OpenLibrary (fallback): {author_name}")
        
        # First, get the author's OpenLibrary key
        author_data = fetch_author_from_openlibrary(author_name)
        
        if not author_data or not author_data.get("openlibrary_key"):
            LOGGER.debug(f"No OpenLibrary key found for author: {author_name}")
            return []
        
        # Extract OpenLibrary author ID from key
        openlibrary_key = author_data["openlibrary_key"]
        LOGGER.info(f"OpenLibrary key: {openlibrary_key}")
        
        # Handle different key formats
        if "/authors/" in openlibrary_key:
            ol_author_id = openlibrary_key.split("/authors/")[1]
            LOGGER.info(f"Extracted OpenLibrary author ID from full path: {ol_author_id}")
        elif openlibrary_key.startswith("OL") and openlibrary_key.endswith("A"):
            ol_author_id = openlibrary_key
            LOGGER.info(f"Using OpenLibrary key directly as author ID: {ol_author_id}")
        else:
            LOGGER.debug(f"Invalid OpenLibrary key format: {openlibrary_key}")
            LOGGER.debug(f"Key does not match expected formats, returning empty")
            return []
        
        # Fetch author's works from OpenLibrary
        works_url = f"https://openlibrary.org/authors/{ol_author_id}/works.json"
        params = {"limit": 10}  # Get up to 10 works
        LOGGER.info(f"Fetching works from: {works_url}")
        
        response = requests.get(works_url, params=params, timeout=5)
        response.raise_for_status()
        
        works_data = response.json()
        LOGGER.info(f"Works response: {works_data}")
        
        if not works_data.get("entries"):
            LOGGER.debug(f"No works found for author: {author_name}")
            return []
        
        LOGGER.info(f"Found {len(works_data['entries'])} works for {author_name}")
        popular_books = []
        
        # Process up to 5 most popular works
        for i, work in enumerate(works_data["entries"][:5]):
            try:
                work_key = work.get("key", "")
                work_title = work.get("title", "Unknown Title")
                
                LOGGER.info(f"Processing work {i}: {work_title} (key: {work_key})")
                
                if not work_key or not work_title:
                    continue
                
                # Extract work ID from key
                if "/works/" in work_key:
                    work_id = work_key.split("/works/")[1]
                else:
                    continue
                
                # Create book object
                book = {
                    "id": work_id,  # Use OpenLibrary work ID
                    "title": work_title,
                    "cover_url": None,  # Will enhance below
                    "author": author_name,
                    "openlibrary_key": work_key,
                    "first_publish_year": work.get("first_publish_year"),
                    "edition_count": work.get("edition_count", 0),
                    "source": "openlibrary"
                }
                
                # Try to get cover using OpenLibrary search
                try:
                    cover_url = get_book_cover_from_openlibrary(work_title, author_name)
                    if cover_url:
                        book["cover_url"] = cover_url
                        LOGGER.info(f"Found cover for {work_title}: {cover_url}")
                    else:
                        # Fallback: Use work ID cover URL
                        book["cover_url"] = f"https://covers.openlibrary.org/w/id/{work_id}-M.jpg"
                        LOGGER.info(f"Using fallback cover for {work_title}: {book['cover_url']}")
                except Exception as e:
                    LOGGER.debug(f"Error getting cover for {work_title}: {e}")
                    # Fallback: Use work ID cover URL
                    book["cover_url"] = f"https://covers.openlibrary.org/w/id/{work_id}-M.jpg"
                
                popular_books.append(book)
                LOGGER.info(f"Added OpenLibrary popular book: {work_title}")
                
            except Exception as e:
                LOGGER.debug(f"Error processing work {i}: {e}")
                continue
        
        LOGGER.info(f"Found {len(popular_books)} popular books for {author_name} via OpenLibrary")
        return popular_books
    
    except requests.Timeout:
        LOGGER.debug(f"Timeout fetching popular books from OpenLibrary: {author_name}")
        return []
    except requests.RequestException as e:
        LOGGER.debug(f"Network error fetching popular books: {e}")
        return []
    except Exception as e:
        LOGGER.error(f"Error fetching popular books from OpenLibrary: {e}")
        return []


def get_author_work_count(author_id: int, author_name: str) -> Optional[int]:
    """
    Get total work count for an author from OpenLibrary.
    
    Args:
        author_id: Author ID (for caching/logging)
        author_name: Author name to search for
    
    Returns:
        int: Total number of works or None if not found
    """
    try:
        LOGGER.info(f"Fetching work count from OpenLibrary: {author_name}")
        
        # Get author data which includes work count
        author_data = fetch_author_from_openlibrary(author_name)
        
        if author_data and author_data.get("work_count") is not None:
            work_count = int(author_data["work_count"])
            LOGGER.info(f"Found {work_count} total works for {author_name}")
            return work_count
        else:
            LOGGER.debug(f"No work count found for author: {author_name}")
            return None
    
    except Exception as e:
        LOGGER.error(f"Error fetching work count from OpenLibrary: {e}")
        return None


def fetch_and_update_all_authors_from_openlibrary() -> dict:
    """
    Fetch and update all authors from OpenLibrary.
    
    Returns:
        dict: Statistics about the operation
    """
    try:
        stats = {
            "authors_checked": 0,
            "authors_updated": 0,
            "errors": 0
        }
        
        # Get all authors
        authors = execute_query("SELECT id, name FROM authors")
        
        if not authors:
            LOGGER.info("No authors to update")
            return stats
        
        stats["authors_checked"] = len(authors)
        
        for author in authors:
            try:
                if update_author_from_openlibrary(author['id'], author['name']):
                    stats["authors_updated"] += 1
            except Exception as e:
                LOGGER.error(f"Error updating author {author['name']}: {e}")
                stats["errors"] += 1
        
        LOGGER.info(f"OpenLibrary author update complete: {stats}")
        return stats
    
    except Exception as e:
        LOGGER.error(f"Error in fetch_and_update_all_authors_from_openlibrary: {e}")
        return {
            "authors_checked": 0,
            "authors_updated": 0,
            "errors": 1
        }
