# format_text_output.py
import re
"""
Formats the parsed church bulletin data into the desired text format
"""

def format_hymn_verse_text(verse_text, verse_num):
    """
    Format hymn verse with verse number at the start.
    
    Input: "Kan. No. 154 \n1. Dhëvaremma madhye\nYirutthiralaagi..."
    Output: "1. Dhëvaremma madhye\nYirutthiralaagi..."
    """
    if not verse_text or verse_text == 'nan':
        return ""
    
    # Remove the header if it exists (Kan. No. XXX)
    lines = verse_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip header lines like "Kan. No. 154" or "Tulu No. 294"
        if re.match(r'^(Kan|Tulu|Eng)\.?\s+No\.?\s+\d+', line, re.I):
            continue
        # Skip standalone verse numbers
        if re.match(r'^\d+\.\s*$', line):
            continue
        formatted_lines.append(line)
    
    # Join and return
    result = '\n'.join(formatted_lines)
    
    # Ensure verse number is at the start
    if not result.startswith(f'{verse_num}.'):
        result = f'{verse_num}. {result}'
    
    return result


def format_church_bulletin(parsed_data, mapping, announcements_table=None):
    """
    Generate formatted text output matching the desired church bulletin format.
    """
    import re
    
    output = []
    
    # Header
    output.append("U.B.M. CHRISTA KANTHI CHURCH, KURLA\n")
    
    # Add service metadata if available
    metadata = parsed_data.get('metadata', {})
    if metadata.get('sunday_name'):
        output.append(metadata['sunday_name'])
    if metadata.get('date'):
        output.append(metadata['date'])
    if metadata.get('service_type'):
        output.append(metadata['service_type'])
    
    # Organist
    organist = parsed_data.get('organist', 'Mr. Osmond')
    output.append(f" Organist: {organist}")
    output.append("* Prelude:")
    output.append("* Invocation: Rev. Sam")
    
    # Process hymns in order
    hymns = parsed_data.get('hymns', [])
    
    # First hymn (opening)
    if len(hymns) > 0:
        hymn = hymns[0]
        output.append(f"* Hymn: {hymn['line']}\n")
        
        # Add hymn verses
        hymn_key = f"HYMN1"
        v_num = 1
        while f'{{{hymn_key}_EN_V{v_num}}}' in mapping or f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
            # Transliteration
            if f'{{{hymn_key}_EN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_EN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            
            # Kannada script
            if f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_KN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            
            v_num += 1
    
    # Adoration section
    output.append("* Adoration, Confession, Absolution, Thanksgiving:")
    
    # Responsive Psalm
    if parsed_data.get('psalm'):
        output.append(f"* Responsive Psalm: {parsed_data['psalm']}\n")
        if parsed_data.get('psalm_en'):
            output.append(parsed_data['psalm_en'])
            output.append("")
    
    # Old Testament Reading
    if parsed_data.get('old_testament'):
        output.append(f"* O.T. Bible Reading: {parsed_data['old_testament']}\n")
        if parsed_data.get('old_testament_en'):
            output.append(parsed_data['old_testament_en'])
            output.append("")
    
    # Second hymn (after OT)
    if len(hymns) > 1:
        hymn = hymns[1]
        output.append(f"* Hymn: {hymn['line']}\n")
        
        hymn_key = f"HYMN2"
        v_num = 1
        while f'{{{hymn_key}_EN_V{v_num}}}' in mapping or f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
            if f'{{{hymn_key}_EN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_EN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            if f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_KN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            v_num += 1
    
    # New Testament Reading
    if parsed_data.get('new_testament'):
        output.append(f"* N.T. Bible Reading: {parsed_data['new_testament']}\n")
        if parsed_data.get('new_testament_en'):
            output.append(parsed_data['new_testament_en'])
            output.append("")
    
    # Gospel Reading
    if parsed_data.get('gospel'):
        output.append(f"* Gospel Reading: {parsed_data['gospel']}\n")
        if parsed_data.get('gospel_en'):
            output.append(parsed_data['gospel_en'])
            output.append("\n")
    
    # Service elements
    output.append("* Apostles Creed:")
    output.append("* Announcements:")
    
    # Announcements text
    if parsed_data.get('announcements_block'):
        ann_text = parsed_data['announcements_block']
        output.append(ann_text)
        output.append("")
    
    # Announcements table
    if announcements_table and len(announcements_table) > 1:
        output.append("")
        output.append(f"{announcements_table[0][0]}\t{announcements_table[0][1]}")
        for row in announcements_table[1:]:
            output.append(f"{row[0]}\t{row[1]}")
        output.append("")
    
    # Offertory hymn
    if len(hymns) > 2:
        hymn = hymns[2]
        output.append(f"* Off. Hymn: {hymn['line']}\n")
        
        hymn_key = f"HYMN3"
        v_num = 1
        while f'{{{hymn_key}_EN_V{v_num}}}' in mapping or f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
            if f'{{{hymn_key}_EN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_EN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            if f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_KN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            v_num += 1
    
    output.append("* Off. Prayer:")
    output.append("* Intercessory Prayer:")
    
    # Praise & Worship hymn
    if len(hymns) > 3:
        hymn = hymns[3]
        output.append(f"* Praise & Worship:/ {hymn['line']}\n")
        
        hymn_key = f"HYMN4"
        v_num = 1
        while f'{{{hymn_key}_EN_V{v_num}}}' in mapping or f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
            if f'{{{hymn_key}_EN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_EN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            if f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_KN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            v_num += 1
    
    # Sermon
    sermon_title = parsed_data.get('sermon_title', 'Unity in Faith and Action')
    gospel_ref = parsed_data.get('gospel', '')
    output.append(f'* Sermon:\n"{sermon_title}" ({gospel_ref})')
    
    # Closing hymn
    if len(hymns) > 4:
        hymn = hymns[4]
        output.append(f"* Hymn: {hymn['line']}\n")
        
        hymn_key = f"HYMN5"
        v_num = 1
        while f'{{{hymn_key}_EN_V{v_num}}}' in mapping or f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
            if f'{{{hymn_key}_EN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_EN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            if f'{{{hymn_key}_KN_V{v_num}}}' in mapping:
                verse_text = format_hymn_verse_text(mapping[f'{{{hymn_key}_KN_V{v_num}}}'], v_num)
                if verse_text:
                    output.append(verse_text)
                    output.append("")
            v_num += 1
    
    output.append("* Lord's Prayer:")
    output.append("* Benediction:")
    output.append("* Threefold Amen:")
    output.append("* Postlude:")
    
    return "\n".join(output)