import os
import pdfplumber
from unittest.mock import MagicMock
import parse_pdf
from build_helpers import build_mapping_wrapper
from generate_pdf import generate_pdf

text = """• Organist: Mr. Osmond 
• Prelude: 
• Invocation: Rev. Sam 
• Hymn: K-154 M.T. 178 (Vs. 1-3) 
• Adoration, Confession, Absolution, Thanksgiving: 
• Responsive Psalm: Psalm 67:1–7 (Ms. Riya) 
• O.T. Bible Reading: Joshua 4:1–11 (Mr. Wilber Joseph) 
• Hymn: K-151 M.T. 41 (Vs. 1 & 3) 
• N.T. Bible Reading: Acts 4:32–37 (Mr. Wilber Joseph) 
• Gospel Reading: Mark 6:32–44 (Mr. Osmond Pengal) 
• Apostles Creed: 
• Announcements: 
• Off. Hymn: K-145 M.T. 28 (Req. Vs.) 
• Off. Prayer: 
• Intercessory Prayer: 
• Praise & Worship:/ K-150 M.T 158 (vs 1&2) 
• Sermon: 
“Unity in Faith and Action” (Mark 6:32–44) 
• Hymn: K-142 M.T. 260 (Vs. 1-3) 
• Lord’s Prayer: 
• Benediction: 
• Threefold Amen: 
• Postlude: 
• Postlude:"""

mock_pdf = MagicMock()
mock_page = MagicMock()
mock_page.extract_text.return_value = text
mock_pdf.__enter__.return_value.pages = [mock_page]

# backup and override
real_open = pdfplumber.open
pdfplumber.open = lambda path: mock_pdf

try:
    parsed = parse_pdf.parse_pdf_to_structured("dummy.pdf")
    print("Parsed data keys:", parsed.keys())
    print("Hymns found:", len(parsed['hymns']))
    print("Psalm:", parsed.get('psalm'))
    print("Old Testament:", parsed.get('old_testament'))
    print("New Testament:", parsed.get('new_testament'))
    print("Gospel:", parsed.get('gospel'))

    mapping, _ = build_mapping_wrapper(parsed, None)
    
    output_path = os.path.join(os.getcwd(), "output_bulletin.pdf")
    generate_pdf(output_path, mapping)
    print("Done! PDF generated at:", output_path)

finally:
    pdfplumber.open = real_open
