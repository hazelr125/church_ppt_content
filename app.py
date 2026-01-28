#app.py
import os
from flask import Flask, request, send_file, render_template, flash, redirect, url_for
from build_helpers import parse_pdf_to_structured, build_mapping_wrapper
from generate_pdf import generate_pdf
from hymns_db import HymnDatabase, process_user_hymns
from parse_announcements import parse_announcements_docx

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "change-this-secret-for-production"

hymn_db = HymnDatabase("kannada_hymns.csv", "tulu_hymns.csv", "english_hymns.csv")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        ann_doc_file = request.files.get('ann_doc')

        if not pdf_file:
            flash("Please upload the weekly PDF.")
            return redirect(url_for('index'))
        
        # Process user hymn selections from the form
        hymn_placeholders = process_user_hymns(request.form, hymn_db)

        print(f"Generated {len(hymn_placeholders)} hymn placeholders")
        for key, value in list(hymn_placeholders.items())[:5]:  # Show first 5
            print(f"  {key}: {str(value)[:50]}...")

        # Save uploaded PDF
        pdf_path = os.path.join(UPLOAD_DIR, 'input.pdf')
        pdf_file.save(pdf_path)

        # Parse the PDF to extract Bible references and other info
        parsed = parse_pdf_to_structured(pdf_path)

        # Build mapping with Bible passages and default hymns from PDF
        mapping, announcements_table = build_mapping_wrapper(parsed, hymn_db)
        
        # Override with user-selected hymns from the form
        mapping.update(hymn_placeholders)
        
        # Handle announcements DOCX if provided
        if ann_doc_file:
            ann_path = os.path.join(UPLOAD_DIR, 'announcements.docx')
            ann_doc_file.save(ann_path)
            ann_table, ann_text = parse_announcements_docx(ann_path)

            # Override announcements text
            parsed['announcements_block'] = ann_text
            mapping['{ANNOUNCEMENTS_TEXT}'] = ann_text

            # Override announcements table if we found one
            if ann_table:
                announcements_table = ann_table

        # Generate output PDF with all content
        output_pdf = os.path.join(UPLOAD_DIR, 'church_content.pdf')
        generate_pdf(output_pdf, mapping, announcements_table_data=announcements_table)

        return send_file(output_pdf, as_attachment=True, download_name='church_content.pdf')

    return render_template('index.html')

if __name__ == "__main__": 
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)