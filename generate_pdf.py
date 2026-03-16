# generate_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Try to register Kannada font if available
KANNADA_FONT_REGISTERED = False
try:
    # Check if Noto Sans Kannada font exists or use Windows default Nirmala
    font_paths = [
        ('/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf', 0),
        ('C:\\Windows\\Fonts\\NotoSansKannada-Regular.ttf', 0),
        ('/System/Library/Fonts/Supplemental/NotoSansKannada-Regular.ttf', 0),
        ('./fonts/NotoSansKannada-Regular.ttf', 0),
        ('./NotoSansKannada-Regular.ttf', 0),
        ('C:\\Windows\\Fonts\\Nirmala.ttc', 0),
        ('C:\\Windows\\Fonts\\tunga.ttf', 0)
    ]
    
    for font_path, sf_index in font_paths:
        if os.path.exists(font_path):
            if font_path.lower().endswith('.ttc'):
                pdfmetrics.registerFont(TTFont('Kannada', font_path, subfontIndex=sf_index))
            else:
                pdfmetrics.registerFont(TTFont('Kannada', font_path))
            KANNADA_FONT_REGISTERED = True
            print(f"Kannada font registered from: {font_path}")
            break
except Exception as e:
    print(f"Could not register Kannada font: {e}")
    print("Kannada text will be rendered with default font (may not display correctly)")


def is_kannada_text(text):
    """Check if text contains Kannada characters"""
    if not text:
        return False
    # Kannada Unicode range: \u0C80-\u0CFF
    return any('\u0C80' <= char <= '\u0CFF' for char in str(text))


def generate_pdf(output_pdf, mapping, announcements_table_data=None):
    """Generate PDF with proper Kannada support"""
    doc = SimpleDocTemplate(
        output_pdf, 
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#1a1a1a')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        leading=14,
        spaceAfter=6
    )
    
    verse_style = ParagraphStyle(
        'VerseStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        leading=13,
        spaceAfter=4,
        leftIndent=10
    )
    
    hymn_style = ParagraphStyle(
        'HymnStyle',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        leading=11,
        spaceAfter=3,
        leftIndent=5
    )
    
    # Kannada style
    if KANNADA_FONT_REGISTERED:
        kannada_style = ParagraphStyle(
            'KannadaStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Kannada',
            leading=13,
            spaceAfter=3,
            leftIndent=5
        )
    else:
        kannada_style = hymn_style
    
    # Header
    if '{HEADER}' in mapping:
        story.append(Paragraph(mapping['{HEADER}'], title_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Bible passages
    sections = [
        ('PSALM', 'Responsive Psalm'),
        ('OT', 'Old Testament Reading'),
        ('NT', 'New Testament Reading'),
        ('GOSPEL', 'Gospel Reading')
    ]
    
    for key, title in sections:
        if f'{{{key}_DES}}' in mapping:
            desc = mapping[f'{{{key}_DES}}']
            story.append(Paragraph(desc, subtitle_style))
            
            if f'{{{key}_EN}}' in mapping:
                text = mapping[f'{{{key}_EN}}']
                # Split and add verses
                lines = text.split('\n')
                for line in lines:
                    if line.strip():
                        story.append(Paragraph(line.strip(), verse_style))
                
                story.append(Spacer(1, 0.15*inch))
    
    # Hymns
    hymn_num = 1
    while f'{{HYMN{hymn_num}_DES}}' in mapping:
        hymn_desc = mapping[f'{{HYMN{hymn_num}_DES}}']
        story.append(Paragraph(f"<b>{hymn_desc}</b>", subtitle_style))
        
        verse_num = 1
        max_verses = 10
        
        while verse_num <= max_verses:
            # Transliteration (EN)
            if f'{{HYMN{hymn_num}_EN_V{verse_num}}}' in mapping:
                verse_text = mapping[f'{{HYMN{hymn_num}_EN_V{verse_num}}}']
                verse_text = clean_hymn_text(verse_text)
                if verse_text:
                    # Use Preformatted to preserve line breaks
                    story.append(Paragraph(verse_text, hymn_style))
                    story.append(Spacer(1, 0.08*inch))
            
            # Kannada (KN)
            if f'{{HYMN{hymn_num}_KN_V{verse_num}}}' in mapping:
                verse_text = mapping[f'{{HYMN{hymn_num}_KN_V{verse_num}}}']
                verse_text = clean_hymn_text(verse_text)
                if verse_text:
                    # Use Kannada style if font available
                    if is_kannada_text(verse_text) and KANNADA_FONT_REGISTERED:
                        story.append(Paragraph(verse_text, kannada_style))
                    else:
                        story.append(Paragraph(verse_text, hymn_style))
                    story.append(Spacer(1, 0.08*inch))
            
            verse_num += 1
        
        story.append(Spacer(1, 0.15*inch))
        hymn_num += 1
    
    # Announcements
    if '{ANNOUNCEMENTS_TEXT}' in mapping:
        ann_text = mapping['{ANNOUNCEMENTS_TEXT}'] or ''
        if ann_text.strip():
            story.append(Paragraph("<b>ANNOUNCEMENTS</b>", subtitle_style))
            paragraphs = ann_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 0.15*inch))
    
    # Announcements table
    if announcements_table_data and len(announcements_table_data) > 1:
        col_widths = [4*inch, 1.5*inch]
        table = Table(announcements_table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"PDF generated successfully: {output_pdf}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise


def clean_hymn_text(text):
    """Clean and format hymn text"""
    if not text or text == 'nan':
        return ""
    
    text = str(text).strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    formatted = '<br/>'.join(lines)
    
    return formatted