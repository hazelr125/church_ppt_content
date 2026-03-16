# build_helpers.py
from parse_pdf import parse_pdf_to_structured
from bible_fetch import fetch_bible_passage
import re
import pandas as pd

def parse_pdf_to_structured_wrapper(path):
    return parse_pdf_to_structured(path)


def parse_verse_selection(verses_str):
    """Parse verse selection string."""
    if not verses_str or verses_str == 'all':
        return []
    
    verse_nums = []
    parts = verses_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            verse_nums.extend(range(int(start), int(end) + 1))
        elif part.isdigit():
            verse_nums.append(int(part))
    
    return sorted(set(verse_nums))


def get_hymn_from_csv(csv_path, hymn_number, verses_requested='all'):
    """
    Read hymn from CSV file - works with ANY CSV structure.
    Returns formatted hymn verses.
    """
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except:
        return None
    
    # Find hymn number column
    hymn_col = None
    verse_col = None
    
    for col in df.columns:
        if 'hymn' in col.lower() or 'number' in col.lower() or col.lower() in ['no', 'num', 'id']:
            hymn_col = col
            break
    
    for col in df.columns:
        if 'verse' in col.lower() or col.lower() in ['v', 'vs']:
            verse_col = col
            break
    
    if not hymn_col:
        return None
    
    # Filter by hymn number
    hymn_data = df[df[hymn_col].astype(str) == str(hymn_number)]
    
    if hymn_data.empty:
        return None
    
    result = {'verses': []}
    
    # Check if the hymn is stored as 1 row with multiple verses in text
    if len(hymn_data) == 1:
        row = hymn_data.iloc[0]
        
        trans_col = None
        native_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'trans' in col_lower or 'roman' in col_lower or 'english' in col_lower or col_lower in ['text', 'lyrics']:
                trans_col = col
                break
                
        for col in df.columns:
            col_lower = col.lower()
            if 'kannada' in col_lower or 'native' in col_lower or 'script' in col_lower or 'tulu' in col_lower:
                native_col = col
                break
                
        if not trans_col:
            text_cols = [c for c in df.columns if c != hymn_col and c != verse_col]
            if text_cols:
                trans_col = text_cols[0]
                if len(text_cols) > 1:
                    native_col = text_cols[1]
                    
        trans_text = str(row[trans_col]) if trans_col and pd.notna(row[trans_col]) else ""
        native_text = str(row[native_col]) if native_col and pd.notna(row[native_col]) else ""
        
        # The CSV might contain literal '\n' instead of actual newlines
        trans_text = trans_text.replace('\\n', '\n')
        native_text = native_text.replace('\\n', '\n')
        
        trans_verses = []
        if trans_text.strip() and trans_text.strip() != 'nan':
            trans_verses = re.split(r'\n\s*\n', trans_text.replace('\r\n', '\n'))
            
        native_verses = []
        if native_text.strip() and native_text.strip() != 'nan':
            native_verses = re.split(r'\n\s*\n', native_text.replace('\r\n', '\n'))
            
            
        # Determine total verses
        total_verses = max(len(trans_verses), len(native_verses))
        
        if verses_requested == 'all':
            verses_to_include = list(range(1, total_verses + 1))
        else:
            verses_to_include = parse_verse_selection(verses_requested)
            
        for i in range(total_verses):
            v_num = i + 1
            if verses_to_include and v_num not in verses_to_include:
                continue
                
            verse_dict = {'verse_num': v_num}
            if i < len(trans_verses) and trans_verses[i].strip():
                verse_dict['transliteration'] = trans_verses[i].strip()
            if i < len(native_verses) and native_verses[i].strip():
                verse_dict['native'] = native_verses[i].strip()
                
            if 'transliteration' in verse_dict or 'native' in verse_dict:
                result['verses'].append(verse_dict)
                
    else:
        # Multiple rows per hymn
        if verses_requested == 'all':
            verses_to_include = list(range(1, len(hymn_data) + 1))
        else:
            verses_to_include = parse_verse_selection(verses_requested)
            
        # Extract verses
        for idx, (_, row) in enumerate(hymn_data.iterrows(), 1):
            if verses_to_include and idx not in verses_to_include:
                continue
            
            verse_dict = {'verse_num': idx}
            
            # Find transliteration column
            for col in df.columns:
                col_lower = col.lower()
                if 'trans' in col_lower or 'roman' in col_lower or 'english' in col_lower or col_lower in ['text', 'lyrics']:
                    verse_dict['transliteration'] = str(row[col])
                    break
            
            # Find native script column
            for col in df.columns:
                col_lower = col.lower()
                if 'kannada' in col_lower or 'native' in col_lower or 'script' in col_lower or 'tulu' in col_lower:
                    verse_dict['native'] = str(row[col])
                    break
            
            # Fallback: use first text columns
            if 'transliteration' not in verse_dict:
                text_cols = [c for c in df.columns if c != hymn_col and c != verse_col]
                if text_cols:
                    verse_dict['transliteration'] = str(row[text_cols[0]])
                    if len(text_cols) > 1:
                        verse_dict['native'] = str(row[text_cols[1]])
            
            result['verses'].append(verse_dict)
            
    return result


def format_hymn_verse(hymn_type, hymn_num, verse_num, verse_text):
    """
    Format hymn verse - SIMPLE format without extra headers.
    Just returns: verse_number. verse_text
    """
    # Clean up text
    verse_text = str(verse_text).strip()
    if verse_text == 'nan' or not verse_text:
        return ""
    
    # Simply format with verse number at start
    lines = verse_text.split('\n')
    formatted_lines = [line.strip() for line in lines if line.strip()]
    
    if not formatted_lines:
        return ""
    
    # Remove existing verse number if present
    first_line = re.sub(r'^\d+\.?\s*', '', formatted_lines[0])
    
    # Add verse number to first line
    result = f"{verse_num}. {first_line}"
    
    # Add remaining lines
    if len(formatted_lines) > 1:
        result += "\n" + "\n".join(formatted_lines[1:])
    
    return result


def build_mapping_wrapper(parsed: dict, hymn_db):
    """Build mapping dictionary from parsed data."""
    mapping = {}
    
    # Header
    mapping['{HEADER}'] = 'Hymns and Bible Verses'
    
    # Bible passages
    if parsed.get('psalm'):
        mapping['{PSALM_DES}'] = f"Responsive Psalm: {parsed['psalm']}"
        mapping['{PSALM_EN}'] = parsed.get('psalm_en', '')
        mapping['{PSALM_KN}'] = parsed.get('psalm_kn', '')
    
    if parsed.get('old_testament'):
        mapping['{OT_DES}'] = f"Old Testament Reading: {parsed['old_testament']}"
        mapping['{OT_EN}'] = parsed.get('old_testament_en', '')
        mapping['{OT_KN}'] = parsed.get('old_testament_kn', '')
    
    if parsed.get('new_testament'):
        mapping['{NT_DES}'] = f"New Testament Reading: {parsed['new_testament']}"
        mapping['{NT_EN}'] = parsed.get('new_testament_en', '')
        mapping['{NT_KN}'] = parsed.get('new_testament_kn', '')
    
    if parsed.get('gospel'):
        mapping['{GOSPEL_DES}'] = f"Gospel Reading: {parsed['gospel']}"
        mapping['{GOSPEL_EN}'] = parsed.get('gospel_en', '')
        mapping['{GOSPEL_KN}'] = parsed.get('gospel_kn', '')
    
    # Announcements
    mapping['{ANNOUNCEMENTS_TEXT}'] = parsed.get('announcements_block') or ''
    
    # Process hymns
    for idx, hymn_info in enumerate(parsed.get('hymns', []), start=1):
        hymn_type = hymn_info['type']
        hymn_num = hymn_info['number']
        verses_requested = hymn_info['verses']
        
        # Determine CSV file
        if hymn_type == 'K':
            csv_file = 'kannada_hymns.csv'
        elif hymn_type == 'T':
            csv_file = 'tulu_hymns.csv'
        else:
            csv_file = 'english_hymns.csv'
        
        # Get hymn data
        hymn_data = get_hymn_from_csv(csv_file, hymn_num, verses_requested)
        
        if hymn_data:
            # Description
            mapping[f'{{HYMN{idx}_DES}}'] = hymn_info.get('line', f'{hymn_type}-{hymn_num}')
            
            # Add verses
            for verse in hymn_data['verses']:
                v_num = verse['verse_num']
                
                # Transliteration
                if 'transliteration' in verse:
                    formatted = format_hymn_verse(
                        hymn_type, hymn_num, v_num, verse['transliteration']
                    )
                    if formatted:
                        mapping[f'{{HYMN{idx}_EN_V{v_num}}}'] = formatted
                
                # Native script
                if 'native' in verse:
                    formatted = format_hymn_verse(
                        hymn_type, hymn_num, v_num, verse['native']
                    )
                    if formatted:
                        mapping[f'{{HYMN{idx}_KN_V{v_num}}}'] = formatted
    
    announcements_table = None
    return mapping, announcements_table