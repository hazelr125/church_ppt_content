#app.py
import os
from flask import Flask, request, send_file, render_template, flash, redirect, url_for, Response
from build_helpers import parse_pdf_to_structured, build_mapping_wrapper
from bible_fetch import fetch_bible_passage
from generate_pdf import generate_pdf
from parse_announcements import parse_announcements_docx
from parse_pdf import to_kannada_ref, format_passage_with_verses
from format_text import format_church_bulletin

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "change-this-secret-for-production"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        ann_doc_file = request.files.get('ann_doc')
        output_format = request.form.get('output_format', 'text')

        if not pdf_file:
            flash("Please upload the weekly PDF.")
            return redirect(url_for('index'))

        # Save uploaded PDF
        pdf_path = os.path.join(UPLOAD_DIR, 'input.pdf')
        pdf_file.save(pdf_path)

        # Parse the PDF
        parsed = parse_pdf_to_structured(pdf_path)

        # Build mapping (pass None for hymn_db since we're reading CSV directly)
        mapping, announcements_table = build_mapping_wrapper(parsed, None)
        
        # Handle announcements DOCX
        if ann_doc_file:
            ann_path = os.path.join(UPLOAD_DIR, 'announcements.docx')
            ann_doc_file.save(ann_path)
            ann_table, ann_text = parse_announcements_docx(ann_path)

            parsed['announcements_block'] = ann_text
            mapping['{ANNOUNCEMENTS_TEXT}'] = ann_text

            if ann_table:
                announcements_table = ann_table

        # Generate output
        if output_format == 'text':
            # Generate text output
            text_output = format_church_bulletin(parsed, mapping, announcements_table)
            
            output_path = os.path.join(UPLOAD_DIR, 'church_content.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_output)
            
            return send_file(output_path, as_attachment=True, download_name='church_content.txt')
        
        else:
            # Generate PDF
            output_pdf = os.path.join(UPLOAD_DIR, 'church_content.pdf')
            generate_pdf(output_pdf, mapping, announcements_table_data=announcements_table)
            return send_file(output_pdf, as_attachment=True, download_name='church_content.pdf')

    return render_template('index.html')


@app.route('/manual', methods=['POST'])
def manual():
    """Handle manual entry of hymns and readings"""
    output_format = request.form.get('output_format', 'text')
    ann_doc_file = request.files.get('ann_doc')

    def build_manual_hymn_line(hymn_type, hymn_number, verses_requested):
        prefix_map = {'K': 'K', 'T': 'T', 'E': 'E'}
        hymn_prefix = prefix_map.get(hymn_type, 'E')
        verse_text = verses_requested if verses_requested else 'all'
        if verse_text.lower() == 'all':
            return f"{hymn_prefix}-{hymn_number} (Req. Vs.)"
        return f"{hymn_prefix}-{hymn_number} (Vs. {verse_text})"
    
    # Construct parsed dictionary manually
    parsed = {
        'hymns': [],
        'psalm': None,
        'old_testament': None,
        'new_testament': None,
        'gospel': None,
        'bulletin_date': None,
        'announcements_block': None
    }
    
    # Extract hymns
    hymn_descs = request.form.getlist('hymn_desc[]')
    hymn_langs = request.form.getlist('hymn_lang[]')
    hymn_nums = request.form.getlist('hymn_num[]')
    hymn_verses = request.form.getlist('hymn_verses[]')
    
    for i in range(len(hymn_nums)):
        if hymn_nums[i].strip():
            language = hymn_langs[i].strip().lower() if i < len(hymn_langs) else 'english'
            hymn_type = {'kannada': 'K', 'tulu': 'T'}.get(language, 'E')
            hymn_number = hymn_nums[i].strip()
            verses_requested = hymn_verses[i].strip() if i < len(hymn_verses) and hymn_verses[i].strip() else 'all'
            parsed['hymns'].append({
                'type': hymn_type,
                'language': language,
                'number': hymn_number,
                'verses': verses_requested,
                'designation': hymn_descs[i].strip() if i < len(hymn_descs) and hymn_descs[i].strip() else f"Hymn {i+1}",
                'line': build_manual_hymn_line(hymn_type, hymn_number, verses_requested),
                'original_text': ""
            })
            
    # Extract readings
    def build_reference(prefix):
        legacy_ref = request.form.get(f'{prefix}_ref', '').strip()
        if legacy_ref:
            return legacy_ref

        book = request.form.get(f'{prefix}_book', '').strip()
        chapter = request.form.get(f'{prefix}_chapter', '').strip()
        start_verse = request.form.get(f'{prefix}_start_verse', '').strip()
        end_verse = request.form.get(f'{prefix}_end_verse', '').strip()

        if not book or not chapter or not start_verse:
            return None

        if end_verse and end_verse != start_verse:
            return f"{book} {chapter}:{start_verse}-{end_verse}"

        return f"{book} {chapter}:{start_verse}"

    def populate_bible_text(reference_key, english_key, kannada_key):
        reference = parsed.get(reference_key)
        if not reference:
            parsed[english_key] = ''
            parsed[kannada_key] = ''
            return

        verses = fetch_bible_passage(reference, 'en')
        parsed[english_key] = format_passage_with_verses(verses, reference)
        parsed[kannada_key] = to_kannada_ref(reference)

    parsed['psalm'] = build_reference('psalm')
    parsed['old_testament'] = build_reference('ot')
    parsed['new_testament'] = build_reference('nt')
    parsed['gospel'] = build_reference('gospel')

    populate_bible_text('psalm', 'psalm_en', 'psalm_kn')
    populate_bible_text('old_testament', 'old_testament_en', 'old_testament_kn')
    populate_bible_text('new_testament', 'new_testament_en', 'new_testament_kn')
    populate_bible_text('gospel', 'gospel_en', 'gospel_kn')
    
    # Build mapping
    mapping, announcements_table = build_mapping_wrapper(parsed, None)
    
    # Handle announcements DOCX
    if ann_doc_file and ann_doc_file.filename:
        ann_path = os.path.join(UPLOAD_DIR, 'announcements.docx')
        ann_doc_file.save(ann_path)
        ann_table, ann_text = parse_announcements_docx(ann_path)

        parsed['announcements_block'] = ann_text
        mapping['{ANNOUNCEMENTS_TEXT}'] = ann_text

        if ann_table:
            announcements_table = ann_table

    # Generate output
    if output_format == 'text':
        text_output = format_church_bulletin(parsed, mapping, announcements_table)
        
        output_path = os.path.join(UPLOAD_DIR, 'church_content_manual.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_output)
        
        return send_file(output_path, as_attachment=True, download_name='church_content_manual.txt')
    
    else:
        output_pdf = os.path.join(UPLOAD_DIR, 'church_content_manual.pdf')
        generate_pdf(output_pdf, mapping, announcements_table_data=announcements_table)
        return send_file(output_pdf, as_attachment=True, download_name='church_content_manual.pdf')



@app.route('/preview', methods=['POST'])
def preview():
    """Preview text output"""
    pdf_file = request.files.get('pdf')
    ann_doc_file = request.files.get('ann_doc')

    if not pdf_file:
        return "No PDF uploaded", 400

    pdf_path = os.path.join(UPLOAD_DIR, 'input.pdf')
    pdf_file.save(pdf_path)

    parsed = parse_pdf_to_structured(pdf_path)
    mapping, announcements_table = build_mapping_wrapper(parsed, None)
    
    if ann_doc_file:
        ann_path = os.path.join(UPLOAD_DIR, 'announcements.docx')
        ann_doc_file.save(ann_path)
        ann_table, ann_text = parse_announcements_docx(ann_path)
        parsed['announcements_block'] = ann_text
        mapping['{ANNOUNCEMENTS_TEXT}'] = ann_text
        if ann_table:
            announcements_table = ann_table

    text_output = format_church_bulletin(parsed, mapping, announcements_table)
    return Response(text_output, mimetype='text/plain; charset=utf-8')


if __name__ == "__main__": 
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)