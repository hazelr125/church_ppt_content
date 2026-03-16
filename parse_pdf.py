# parse_pdf.py
import pdfplumber
import re
from kannada_bible_map import ENGLISH_TO_KANNADA_BOOKS, ENGLISH_TO_KANNADA_PREFIX, to_kannada_numerals
from bible_fetch import fetch_bible_passage
from bible_normalize import normalize_book


def to_kannada_ref(ref: str) -> str:
    """
    Convert 'Nehemiah 8:1-8' -> 'ನೆಹೆಮಿಯ ೮:೧-೮'
    """
    if not ref:
        return ""

    m = re.match(r"([1-3]?\s?[A-Za-z][A-Za-z\s\.]+?)\s+(\d+:\d+(?:-\d+)?)", ref)
    if not m:
        return ref

    book, verses = m.groups()
    book_clean = normalize_book(book)
    kn_book = ENGLISH_TO_KANNADA_BOOKS.get(book_clean, book_clean)
    kn_prefix = ENGLISH_TO_KANNADA_PREFIX.get(book_clean, "")
    return f"{kn_prefix}{kn_book} {to_kannada_numerals(verses)}"


def extract_metadata(lines):
    """Extract service metadata"""
    metadata = {
        'church_name': 'U.B.M. CHRISTA KANTHI CHURCH, KURLA',
        'date': '',
        'service_type': '',
        'sunday_name': ''
    }
    
    for line in lines[:10]:
        # Date
        date_match = re.search(r'(\d{1,2}(?:ST|ND|RD|TH)?\s+[A-Z]+,?\s+\d{4})', line, re.I)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Service type
        if re.search(r'(KANNADA|ENGLISH|TULU)\s+SERVICE', line, re.I):
            metadata['service_type'] = line.strip()
        
        # Sunday name
        if re.search(r'\d+(?:ST|ND|RD|TH)\s+SUNDAY', line, re.I):
            metadata['sunday_name'] = line.strip()
    
    return metadata


def parse_hymn_info(line):
    """
    Parse hymn line to extract info.
    Returns: (hymn_type, hymn_number, verses_requested, full_line)
    """
    hymn_type = None
    hymn_number = None
    verses = 'all'
    
    # Extract K- or T- hymn
    k_match = re.search(r'K-?\s*(\d+)', line, re.I)
    t_match = re.search(r'T-?\s*(\d+)', line, re.I)
    
    if k_match:
        hymn_type = 'K'
        hymn_number = k_match.group(1)
    elif t_match:
        hymn_type = 'T'
        hymn_number = t_match.group(1)
    
    # Extract verses
    vs_match = re.search(r'\(Vs\.?\s*([\d,\s&-]+)\)', line, re.I)
    if vs_match:
        verses = vs_match.group(1).replace('&', ',').replace(' ', '')
    elif re.search(r'\(Req\.?\s*Vs\.?\)', line, re.I):
        verses = 'all'
    
    return hymn_type, hymn_number, verses


def format_passage_with_verses(passages, reference):
    """Format Bible passages with verse numbers."""
    if not passages:
        return ""
    
    # Extract starting verse number
    match = re.search(r':(\d+)', reference)
    start_verse = int(match.group(1)) if match else 1
    
    formatted = []
    for i, verse_text in enumerate(passages):
        verse_num = start_verse + i
        formatted.append(f"{verse_num} {verse_text}")
    
    return "\n".join(formatted)


def parse_pdf_to_structured(pdf_path: str) -> dict:
    """Main parsing function - extracts all bulletin information from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Normalize lines
    lines = [re.sub(r'^[\s\-\u2022\*]+', '', l).strip() for l in text.splitlines() if l.strip()]

    # Extract metadata
    metadata = extract_metadata(lines)

    data = {
        'metadata': metadata,
        'hymns': [],  # List of dicts with hymn info
        'psalm_en': "",
        'psalm_kn': "",
        'old_testament_en': "",
        'old_testament_kn': "",
        'new_testament_en': "",
        'new_testament_kn': "",
        'gospel_en': "",
        'gospel_kn': "",
        'psalm': "",
        'old_testament': "",
        'new_testament': "",
        'gospel': "",
        'announcements_block': "",
        'birthday_names': [],
        'anniversary_names': [],
        'sermon_title': '',
        'organist': '',
        'readers': {}
    }

    # Patterns
    bible_verse_pattern = re.compile(r'([1-3]?\s?[A-Za-z]+\.?\s*\d{1,3}:\d+(?:-\d+)?)', re.I)
    psalm_pattern = re.compile(r'Psalm\s*([0-9]{1,3}:\d+(?:-\d+)?)', re.I)

    # Scan lines
    i = 0
    while i < len(lines):
        ln = lines[i]
        
        # Organist
        if re.search(r'Organist:', ln, re.I):
            org_match = re.search(r'Organist:\s*(.+)', ln, re.I)
            if org_match:
                data['organist'] = org_match.group(1).strip()
        
        # Hymns (K- or T-)
        if re.search(r'(Hymn|Off\.?\s*Hymn|Praise)', ln, re.I) and re.search(r'[KT]-?\s*\d+', ln, re.I):
            h_type, h_num, h_verses = parse_hymn_info(ln)
            if h_type and h_num:
                data['hymns'].append({
                    'type': h_type,
                    'number': h_num,
                    'verses': h_verses,
                    'line': ln.strip()
                })
            i += 1
            continue

        # Psalm
        m_ps = psalm_pattern.search(ln)
        if m_ps and not data['psalm']:
            ref = "Psalm " + m_ps.group(1)
            data['psalm'] = ref
            
            # Reader
            reader_match = re.search(r'\(([^)]+)\)', ln)
            if reader_match:
                data['readers']['psalm'] = reader_match.group(1)
            
            # Fetch passage
            passages = fetch_bible_passage(ref, "en")
            data['psalm_en'] = format_passage_with_verses(passages, ref)
            data['psalm_kn'] = to_kannada_ref(ref)
            i += 1
            continue

        # Old Testament
        if re.search(r'Old Testament|O\.?T\.?\s+Bible', ln, re.I):
            mv = bible_verse_pattern.search(ln)
            if not mv and i+1 < len(lines):
                mv = bible_verse_pattern.search(lines[i+1])
            
            if mv:
                ref = mv.group(1)
                data['old_testament'] = ref
                
                reader_match = re.search(r'\(([^)]+)\)', ln)
                if reader_match:
                    data['readers']['old_testament'] = reader_match.group(1)
                
                passages = fetch_bible_passage(ref, "en")
                data['old_testament_en'] = format_passage_with_verses(passages, ref)
                data['old_testament_kn'] = to_kannada_ref(ref)
            i += 1
            continue

        # New Testament
        if re.search(r'New Testament|N\.?T\.?\s+Bible', ln, re.I):
            mv = bible_verse_pattern.search(ln)
            if not mv and i+1 < len(lines):
                mv = bible_verse_pattern.search(lines[i+1])
            
            if mv:
                ref = mv.group(1)
                data['new_testament'] = ref
                
                reader_match = re.search(r'\(([^)]+)\)', ln)
                if reader_match:
                    data['readers']['new_testament'] = reader_match.group(1)
                
                passages = fetch_bible_passage(ref, "en")
                data['new_testament_en'] = format_passage_with_verses(passages, ref)
                data['new_testament_kn'] = to_kannada_ref(ref)
            i += 1
            continue

        # Gospel
        if re.search(r'Gospel\s+Reading|Gospel', ln, re.I):
            mv = bible_verse_pattern.search(ln)
            if not mv and i+1 < len(lines):
                mv = bible_verse_pattern.search(lines[i+1])
            
            if mv:
                ref = mv.group(1)
                data['gospel'] = ref
                
                reader_match = re.search(r'\(([^)]+)\)', ln)
                if reader_match:
                    data['readers']['gospel'] = reader_match.group(1)
                
                passages = fetch_bible_passage(ref, "en")
                data['gospel_en'] = format_passage_with_verses(passages, ref)
                data['gospel_kn'] = to_kannada_ref(ref)
            i += 1
            continue
        
        # Sermon
        if re.search(r'Sermon:', ln, re.I):
            if i+1 < len(lines):
                sermon_line = lines[i+1].strip().strip('"\'')
                data['sermon_title'] = sermon_line
            i += 1
            continue

        # Announcements
        if re.match(r'ANNOUNCEMENTS', ln, re.I):
            j = i+1
            block = []
            while j < len(lines):
                nxt = lines[j]
                if re.match(r'^(Praise|Off|Hymn|Lord\'s Prayer|Particulars)', nxt, re.I):
                    break
                block.append(nxt)
                j += 1
            data['announcements_block'] = "\n".join(block).strip()
            i = j
            continue

        # Birthdays
        if re.search(r'Happy Birthday|Birthday', ln, re.I):
            j = i+1
            names = []
            while j < len(lines) and lines[j].strip():
                if re.match(r'^(Happy|Anniversary|Praise|Hymn)', lines[j], re.I):
                    break
                names.append(lines[j].strip())
                j += 1
            data['birthday_names'].extend(names[:20])
            i = j
            continue

        # Anniversaries
        if re.search(r'Happy Anniversary|Anniversary', ln, re.I):
            j = i+1
            names = []
            while j < len(lines) and lines[j].strip():
                if re.match(r'^(Happy|Birthday|Praise|Hymn)', lines[j], re.I):
                    break
                names.append(lines[j].strip())
                j += 1
            data['anniversary_names'].extend(names[:20])
            i = j
            continue
        
        i += 1

    return data


def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)