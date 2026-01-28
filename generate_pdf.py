# generate_pdf.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register custom fonts (like Kannada)
# pdfmetrics.registerFont(TTFont('NotoSansKannada', 'NotoSansKannada-Regular.ttf'))

def generate_pdf(output_pdf, mapping, announcements_table_data=None):
    """
    Generate a PDF document from the mapping data
    """
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Create custom styles matching your PPT styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=60,
        fontName='Times-Roman',
        alignment=1  # Center
    )
    
    verse_style = ParagraphStyle(
        'VerseStyle',
        parent=styles['Normal'],
        fontSize=50,
        fontName='Helvetica'
    )
    
    # Process each section
    if '{WELCOME}' in mapping:
        story.append(Paragraph(mapping['{WELCOME}'], title_style))
        story.append(Spacer(1, 0.5*inch))
    
    # Add Bible passages
    for key in ['PSALM', 'OT', 'NT', 'GOSPEL']:
        if f'{{{key}_DES}}' in mapping:
            story.append(Paragraph(mapping[f'{{{key}_DES}}'], title_style))
            story.append(PageBreak())
    
    # Add hymns verses
    hymn_num = 1
    while f'{{HYMN{hymn_num}_DES}}' in mapping:
        story.append(Paragraph(mapping[f'{{HYMN{hymn_num}_DES}}'], title_style))
        
        # Add verses
        verse_num = 1
        for lang in ['EN', 'KN']:
            while f'{{HYMN{hymn_num}_{lang}_V{verse_num}}}' in mapping:
                verse_text = mapping[f'{{HYMN{hymn_num}_{lang}_V{verse_num}}}']
                story.append(Paragraph(verse_text, verse_style))
                story.append(Spacer(1, 0.3*inch))
                verse_num += 1
        
        story.append(PageBreak())
        hymn_num += 1
    
    # Add announcements
    if '{ANNOUNCEMENTS_TEXT}' in mapping:
        story.append(Paragraph("Announcements", title_style))
        story.append(Paragraph(mapping['{ANNOUNCEMENTS_TEXT}'], styles['Normal']))
    
    # Add announcements table
    if announcements_table_data:
        table = Table(announcements_table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)