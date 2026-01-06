#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-powered book recommendations system.
Migrated from the old frontend with existing AI prompts and logic.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional

from backend.base.logging import LOGGER
from backend.internals.db import execute_query


def get_ai_provider_manager():
    """Get the AI provider manager instance."""
    try:
        from backend.features.ai_providers.manager import initialize_ai_providers
        return initialize_ai_providers()
    except ImportError as e:
        LOGGER.warning(f"AI providers not available: {e}")
        return None


def get_popular_manga_this_week() -> List[Dict[str, Any]]:
    """
    Get popular manga for this week from trending_manga table.
    
    This function retrieves trending manga from the database that were
    populated from AniList data.
    
    Returns:
        List of popular manga dictionaries with metadata.
    """
    try:
        # Get trending manga from the database
        query = """
        SELECT anilist_id, title, cover_url, trending_score, 
               popularity, description, created_at
        FROM trending_manga 
        ORDER BY trending_score DESC, popularity DESC 
        LIMIT 10
        """
        
        results = execute_query(query)
        if not results:
            LOGGER.info("No trending manga found")
            return []
        
        # Convert to list of dictionaries with proper field names
        popular_manga = []
        for row in results:
            manga_dict = {
                'id': None,  # No library ID, this is from AniList
                'metadata_id': row['anilist_id'],
                'name': row['title'],
                'title': row['title'],
                'author': 'Unknown',  # AniList data doesn't include author in this table
                'publisher': 'Unknown',
                'published_date': 'Unknown',
                'isbn': 'Unknown',
                'subjects': ['Manga', 'Japanese'],
                'description': row['description'] or 'No description available',
                'cover_url': row['cover_url'] or '/assets/img/no-cover.png',
                'metadata_source': 'AniList',
                'content_type': 'manga',
                'star_rating': 0,
                'trending_score': row['trending_score'],
                'popularity': row['popularity']
            }
            popular_manga.append(manga_dict)
        
        LOGGER.info(f"Retrieved {len(popular_manga)} trending manga")
        return popular_manga
        
    except Exception as e:
        LOGGER.error(f"Error getting popular manga: {e}")
        return []


def get_popular_books_this_week() -> List[Dict[str, Any]]:
    """
    Get popular books for this week using AI recommendations.
    
    This function generates popular books by analyzing recent trends
    and using AI to recommend books that are currently popular.
    
    Returns:
        List of popular book dictionaries with metadata.
    """
    try:
        ai_manager = get_ai_provider_manager()
        if not ai_manager or not ai_manager.get_all_providers():
            LOGGER.info("No AI providers available, returning empty popular books")
            return []
        
        # Get a sample of recent books to analyze for trends
        recent_books = _get_recent_books_sample()
        if not recent_books:
            LOGGER.info("No recent books found for trend analysis")
            return []
        
        # Use AI to generate popular books based on recent trends
        popular_books = _get_ai_popular_books(recent_books, ai_manager)
        
        # Enhance with metadata from providers
        enhanced_books = []
        for book in popular_books[:10]:  # Limit to 10 popular books
            book_data = _search_and_fetch_book(book['title'], book['author'])
            if book_data:
                enhanced_books.append(book_data)
        
        LOGGER.info(f"Generated {len(enhanced_books)} popular books for this week")
        return enhanced_books
        
    except Exception as e:
        LOGGER.error(f"Error getting popular books: {e}")
        return []


def get_ai_book_recommendations(book_id: int) -> List[Dict[str, Any]]:
    """
    Get AI-powered book recommendations based on a specific book.
    
    Args:
        book_id: The book ID (series ID)
        
    Returns:
        List of recommended book dictionaries.
    """
    try:
        # Get book details - try different column names
        book = None
        for column_name in ['name', 'title']:
            try:
                book_result = execute_query(f"""
                    SELECT id, {column_name} as title, author, subjects, star_rating, 
                           user_description, reading_progress, metadata_source
                    FROM series 
                    WHERE id = ? AND content_type = 'BOOK'
                """, (book_id,))
                
                if book_result:
                    book = book_result[0]
                    break
            except Exception as e:
                LOGGER.debug(f"Failed to query with column '{column_name}': {e}")
                continue
        
        if not book:
            LOGGER.warning(f"Book {book_id} not found")
            return []
        
        # Check if cached recommendations exist and are still valid
        cached_recs = _get_cached_recommendations(book_id, book)
        if cached_recs is not None:
            LOGGER.info(f"Using cached recommendations for book {book_id}")
            return cached_recs['recommendations']
        
        # Try AI-powered recommendations
        ai_manager = get_ai_provider_manager()
        recommendations = []
        
        if ai_manager and ai_manager.get_all_providers():
            recommendations = _get_ai_book_recommendations_internal(book, ai_manager)
        
        # If AI recommendations failed or returned empty, fall back to category-only
        if not recommendations:
            LOGGER.info(f"Falling back to category-only recommendations for book {book_id}")
            recommendations = _get_category_recommendations(book)
        
        # Cache the recommendations
        _cache_recommendations(book_id, recommendations, "ai" if recommendations else "category", book)
        
        LOGGER.info(f"Generated {len(recommendations)} recommendations for book {book_id}")
        return recommendations
        
    except Exception as e:
        LOGGER.error(f"Error getting AI recommendations for book {book_id}: {e}")
        return []


def _get_recent_books_sample() -> List[Dict[str, Any]]:
    """Get a sample of recent books for trend analysis."""
    try:
        result = execute_query("""
            SELECT id, name as title, author, subjects, star_rating, 
                   created_at, updated_at
            FROM series 
            WHERE content_type = 'BOOK' 
            ORDER BY updated_at DESC 
            LIMIT 20
        """)
        
        return [dict(row) for row in result] if result else []
    except Exception as e:
        LOGGER.error(f"Error getting recent books sample: {e}")
        # Try with different column name
        try:
            result = execute_query("""
                SELECT id, title, author, subjects, star_rating, 
                       created_at, updated_at
                FROM series 
                WHERE content_type = 'BOOK' 
                ORDER BY updated_at DESC 
                LIMIT 20
            """)
            
            return [dict(row) for row in result] if result else []
        except Exception as e2:
            LOGGER.error(f"Error getting recent books sample with title column: {e2}")
            return []


def _get_ai_popular_books(recent_books: List[Dict[str, Any]], ai_manager) -> List[Dict[str, Any]]:
    """Generate popular books using AI based on recent trends."""
    try:
        # Analyze trends from recent books
        popular_genres = _analyze_popular_genres(recent_books)
        popular_authors = _analyze_popular_authors(recent_books)
        
        # Build AI prompt for popular books
        prompt = f"""Based on current reading trends, recommend 8-10 popular books for this week.

Trending Genres: {', '.join(popular_genres[:5])}
Trending Authors: {', '.join(popular_authors[:3])}

Please recommend popular books that are currently trending. Consider:
- Books by trending authors
- Books in popular genres  
- Recently released books getting attention
- Books with high user engagement

Please provide recommendations in this exact format:
Book Title | Author Name

Only provide the title and author, one per line. No additional text."""
        
        # Get AI response
        provider = ai_manager.get_all_providers()[0] if ai_manager.get_all_providers() else None
        if not provider:
            LOGGER.warning("No AI providers available for popular books")
            return []
        
        response_text = _call_ai_provider(provider, prompt)
        if not response_text:
            LOGGER.warning("AI provider returned empty response for popular books")
            return []
        
        # Parse AI response
        recommendations = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                recommendations.append({
                    'title': parts[0],
                    'author': parts[1]
                })
        
        return recommendations
        
    except Exception as e:
        LOGGER.error(f"Error getting AI popular books: {e}")
        return []


def _get_ai_book_recommendations_internal(book: Dict[str, Any], ai_manager) -> List[Dict[str, Any]]:
    """Generate book recommendations using AI (internal function)."""
    try:
        # Build AI prompt (using the exact same prompt from old frontend)
        title = book.get('title', 'Unknown')
        author = book.get('author', 'Unknown')
        subjects = book.get('subjects', '')
        star_rating = book.get('star_rating', 0)
        user_notes = book.get('user_description', '')
        reading_progress = book.get('reading_progress', 0)
        
        # Parse subjects
        genres_list = []
        if subjects and isinstance(subjects, str):
            genres_list = [g.strip() for g in subjects.split(',') if g.strip()]
        
        genres_str = ', '.join(genres_list) if genres_list else 'Fiction'
        
        # Build prompt with all available information (exact same as old frontend)
        prompt = f"""Based on the following book details, recommend 5-8 similar books.
        
Book Title: {title}
Author: {author}
Genres/Subjects: {genres_str}
User Rating: {star_rating}/5
Reading Progress: {reading_progress}%"""
        
        if user_notes:
            prompt += f"\nUser Notes: {user_notes}"
        
        prompt += """

Please provide recommendations in this exact format:
Book Title | Author Name

Only provide the title and author, one per line. No additional text."""
        
        # Get AI response
        provider = ai_manager.get_all_providers()[0] if ai_manager.get_all_providers() else None
        if not provider:
            LOGGER.warning("No AI providers available")
            return []
        
        response_text = _call_ai_provider(provider, prompt)
        if not response_text:
            LOGGER.warning("AI provider returned empty response")
            return []
        
        # Parse AI response to extract book titles and authors
        recommendations = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                rec_title = parts[0]
                rec_author = parts[1]
                
                # Search for the book in metadata providers
                book_data = _search_and_fetch_book(rec_title, rec_author, book.get('metadata_source'))
                if book_data:
                    recommendations.append(book_data)
        
        LOGGER.info(f"AI generated {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        LOGGER.error(f"Error in AI book recommendations: {e}")
        return []


def _call_ai_provider(provider, prompt: str) -> str:
    """Call AI provider with the given prompt."""
    try:
        response_text = ""
        
        if provider.name == "Groq" and hasattr(provider, 'client'):
            # Groq uses client.chat.completions.create()
            response = provider.client.chat.completions.create(
                model=provider.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a book recommendation expert. Provide book recommendations based on the given details."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            )
            response_text = response.choices[0].message.content
        elif provider.name == "Gemini" and hasattr(provider, 'client'):
            # Gemini uses client.generate_content()
            response = provider.client.generate_content(prompt)
            response_text = response.text
        elif provider.name == "DeepSeek" and hasattr(provider, 'client'):
            # DeepSeek uses client.chat.completions.create()
            response = provider.client.chat.completions.create(
                model=provider.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a book recommendation expert. Provide book recommendations based on the given details."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            )
            response_text = response.choices[0].message.content
        elif provider.name == "Ollama" and hasattr(provider, 'client'):
            # Ollama uses client.generate()
            response = provider.client.generate(model=provider.model, prompt=prompt)
            response_text = response.get('response', '')
        else:
            LOGGER.warning(f"AI provider {provider.name} is not supported for recommendations")
            return ""
        
        return response_text
        
    except Exception as e:
        LOGGER.error(f"Error calling AI provider {provider.name}: {e}")
        return ""


def _analyze_popular_genres(recent_books: List[Dict[str, Any]]) -> List[str]:
    """Analyze popular genres from recent books."""
    genre_count = {}
    
    for book in recent_books:
        subjects = book.get('subjects', '')
        if subjects and isinstance(subjects, str):
            genres = [g.strip() for g in subjects.split(',') if g.strip()]
            for genre in genres:
                genre_count[genre] = genre_count.get(genre, 0) + 1
    
    # Sort by count and return top genres
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    return [genre for genre, count in sorted_genres]


def _analyze_popular_authors(recent_books: List[Dict[str, Any]]) -> List[str]:
    """Analyze popular authors from recent books."""
    author_count = {}
    
    for book in recent_books:
        author = book.get('author', '').strip()
        if author:
            author_count[author] = author_count.get(author, 0) + 1
    
    # Sort by count and return top authors
    sorted_authors = sorted(author_count.items(), key=lambda x: x[1], reverse=True)
    return [author for author, count in sorted_authors]


def _get_category_recommendations(book: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get category-based recommendations (fallback from old frontend)."""
    try:
        subjects = book.get('subjects', '')
        if not subjects:
            return []
        
        # Parse subjects
        genres_list = []
        if subjects and isinstance(subjects, str):
            genres_list = [g.strip() for g in subjects.split(',') if g.strip()]
        
        if not genres_list:
            return []
        
        # Build query to find books with matching subjects/genres
        recommendations = []
        book_id = book.get('id')
        
        for genre in genres_list:
            # Try different column names for title
            for title_column in ['name', 'title']:
                try:
                    results = execute_query(f"""
                        SELECT id, {title_column} as title, author, subjects, star_rating, metadata_source
                        FROM series 
                        WHERE content_type = 'BOOK' 
                        AND id != ? 
                        AND subjects LIKE ?
                        ORDER BY star_rating DESC, RANDOM()
                        LIMIT 5
                    """, (book_id, f'%{genre}%'))
                    
                    if results:
                        recommendations.extend(results)
                        break  # Found results with this column name
                except Exception as e:
                    LOGGER.debug(f"Failed category query with column '{title_column}': {e}")
                    continue
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['id'] not in seen_ids:
                seen_ids.add(rec['id'])
                unique_recommendations.append(rec)
        
        # Limit to 10 recommendations
        return unique_recommendations[:10]
        
    except Exception as e:
        LOGGER.error(f"Error getting category recommendations: {e}")
        return []


def _search_and_fetch_book(title: str, author: str, preferred_source: str = None) -> Optional[Dict[str, Any]]:
    """Search for a book in metadata providers and fetch detailed information."""
    try:
        # Try to find the book in our database first
        result = execute_query("""
            SELECT id, title, author, subjects, star_rating, 
                   cover_url, metadata_source, metadata_id
            FROM series 
            WHERE content_type = 'BOOK' 
            AND (LOWER(title) LIKE LOWER(?) OR LOWER(title) LIKE LOWER(?))
            AND (LOWER(author) LIKE LOWER(?) OR author IS NULL)
            LIMIT 1
        """, (f'%{title}%', f'%{title}%', f'%{author}%'))
        
        if result:
            book_data = dict(result[0])
            # Add cover URL if available
            if not book_data.get('cover_url'):
                book_data['cover_url'] = '/static/img/no-cover.png'
            return book_data
        
        # If not found in database, try metadata providers
        # This would involve calling the metadata API, but for now return a basic entry
        return {
            'id': None,
            'title': title,
            'author': author,
            'subjects': '',
            'star_rating': 0,
            'cover_url': '/static/img/no-cover.png',
            'metadata_source': 'ai_generated',
            'metadata_id': None
        }
        
    except Exception as e:
        LOGGER.error(f"Error searching for book '{title}' by '{author}': {e}")
        return None


def _get_cached_recommendations(book_id: int, book: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get cached recommendations if they're still valid."""
    try:
        # Create a hash of book details to detect changes
        book_hash = _hash_book_details(book)
        
        # Check if cached recommendations exist
        cache_result = execute_query("""
            SELECT recommendations, method, book_hash
            FROM recommendation_cache
            WHERE book_id = ?
        """, (book_id,))
        
        if cache_result:
            cached = cache_result[0]
            # If book details haven't changed, return cached recommendations
            if cached['book_hash'] == book_hash:
                return {
                    'recommendations': json.loads(cached['recommendations']),
                    'method': cached['method']
                }
        
        return None
    except Exception as e:
        LOGGER.debug(f"Error getting cached recommendations: {e}")
        return None


def _cache_recommendations(book_id: int, recommendations: List[Dict[str, Any]], method: str, book: Dict[str, Any]):
    """Cache recommendations for a book."""
    try:
        book_hash = _hash_book_details(book)
        recommendations_json = json.dumps(recommendations)
        
        # Insert or update cache
        execute_query("""
            INSERT OR REPLACE INTO recommendation_cache 
            (book_id, recommendations, method, book_hash, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (book_id, recommendations_json, method, book_hash), commit=True)
        
        LOGGER.debug(f"Cached {len(recommendations)} recommendations for book {book_id}")
        
    except Exception as e:
        LOGGER.error(f"Error caching recommendations: {e}")


def _hash_book_details(book: Dict[str, Any]) -> str:
    """Create a hash of book details to detect changes."""
    try:
        # Include relevant fields in the hash
        relevant_fields = {
            'title': book.get('title', ''),
            'author': book.get('author', ''),
            'subjects': book.get('subjects', ''),
            'star_rating': book.get('star_rating', 0),
            'user_description': book.get('user_description', ''),
            'reading_progress': book.get('reading_progress', 0)
        }
        
        # Create hash string
        hash_string = json.dumps(relevant_fields, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
        
    except Exception as e:
        LOGGER.error(f"Error creating book hash: {e}")
        return hashlib.md5(str(book.get('id', '')).encode()).hexdigest()
