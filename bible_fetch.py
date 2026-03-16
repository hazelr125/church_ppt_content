# bible_fetch.py
import requests
import re
from bible_normalize import normalize_book

def parse_verse_range(verse_str):
    """
    Parse verse range like "1-7" or "32-44" into start and end.
    Returns: (start_verse, end_verse)
    """
    if '-' in verse_str or '–' in verse_str:
        # Handle both hyphen and en-dash
        parts = re.split(r'[-–]', verse_str)
        start = int(parts[0].strip())
        end = int(parts[1].strip())
        return start, end
    else:
        verse = int(verse_str.strip())
        return verse, verse


def fetch_bible_passage(reference: str, language: str = "en") -> list:
    """
    Fetch Bible passage from API, handling verse ranges.
    
    Examples:
        "Psalm 67:1-7" -> fetches verses 1 through 7
        "Mark 6:32-44" -> fetches verses 32 through 44
        "Joshua 4:1-11" -> fetches verses 1 through 11
    
    Returns: List of verse texts
    """
    try:
        # Parse the reference
        # Format: "Book Chapter:Verse" or "Book Chapter:StartVerse-EndVerse"
        match = re.match(r'([1-3]?\s?[A-Za-z\s]+?)\s*(\d+):(\d+(?:[-–]\d+)?)', reference.strip())
        
        if not match:
            print(f"Could not parse reference: {reference}")
            return []
        
        book_name = match.group(1).strip()
        chapter = match.group(2)
        verse_range = match.group(3)
        
        # Parse verse range
        if '-' in verse_range or '–' in verse_range:
            start_verse, end_verse = parse_verse_range(verse_range)
        else:
            start_verse = end_verse = int(verse_range)
        
        # Normalize book name
        book_name = normalize_book(book_name)
        
        # Fetch all verses in range
        verses = []
        for verse_num in range(start_verse, end_verse + 1):
            verse_ref = f"{book_name} {chapter}:{verse_num}"
            
            # Call API
            url = f"https://bible-api.com/{verse_ref}?translation=kjv"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                verse_text = data.get('text', '').strip()
                
                # Clean up verse text
                verse_text = verse_text.replace('\n', ' ')
                verse_text = re.sub(r'\s+', ' ', verse_text)
                
                if verse_text:
                    verses.append(verse_text)
            else:
                print(f"Failed to fetch {verse_ref}: Status {response.status_code}")
        
        return verses
    
    except Exception as e:
        print(f"Error fetching Bible passage '{reference}': {e}")
        return []


def fetch_bible_passage_bulk(reference: str) -> str:
    """
    Fetch Bible passage using bulk API call (alternative method).
    Some APIs support fetching ranges in one call.
    """
    try:
        # Try bible-api.com format
        url = f"https://bible-api.com/{reference}?translation=kjv"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if it's a single verse or multiple
            if 'verses' in data:
                # Multiple verses
                verses = []
                for verse_data in data['verses']:
                    text = verse_data.get('text', '').strip()
                    text = text.replace('\n', ' ')
                    text = re.sub(r'\s+', ' ', text)
                    verses.append(text)
                return verses
            else:
                # Single verse
                text = data.get('text', '').strip()
                text = text.replace('\n', ' ')
                text = re.sub(r'\s+', ' ', text)
                return [text]
        
        return []
    
    except Exception as e:
        print(f"Error in bulk fetch: {e}")
        return []