Church PPT Automation using Python
🕊️ Overview

This project automates the process of creating presentation slides for church services. It reduces the manual effort of copying and formatting content into PowerPoint slides by automatically generating the slides from a predefined content file or text input.

With this automation, the time required to make the weekly church PPTs is reduced by 70–80%, making the process more efficient and consistent.

⚙️ Features

📄 Automatically generates PowerPoint slides from text or song files

🖋️ Custom formatting (fonts, sizes, slide backgrounds, and layouts)

🕒 Reduces time spent on manual PPT creation by up to 80%

💾 Exports directly to .pptx format

🧠 Built using Python and the python-pptx library

🧰 Tech Stack

Language: Python

Libraries:

python-pptx – for creating and editing PowerPoint files

os and pathlib – for file management

(Add others if you used them, e.g. tkinter, pandas, etc.)

🖥️ How It Works

Input your content (e.g., song lyrics, announcements, sermon notes) in a text file.

Run the Python script.

The script automatically:

Reads the input file

Creates slides for each section or song

Formats the text according to preset slide designs

Outputs a ready-to-use PowerPoint presentation (.pptx).

🪄 Example

Input file:

Song Title: Amazing Grace
Verse 1:
Amazing grace, how sweet the sound
That saved a wretch like me


Generated PPT:

Title Slide: "Amazing Grace"

Content Slide: Verse 1 text formatted neatly

🚀 Setup Instructions

Clone the repository:

git clone https://github.com/yourusername/church-ppt-automation.git


Install dependencies:

pip install python-pptx


Run the script:

python main.py


Check the output/ folder for the generated .pptx file.

🧩 Customization

Edit template.pptx to change slide backgrounds or themes.

Modify the Python code to adjust:

Font size

Text color

Layout structure

File reading logic

📊 Impact

Before automation: ~45 minutes per PPT
After automation: ~10 minutes per PPT
⏱️ Time saved: ~70–80%

🧑‍💻 Author

Hazel Ratna
Project developed to streamline weekly church presentation creation using Python automation.

🕯️ Future Enhancements

GUI-based interface for easy content input

Integration with Google Sheets or online song repositories

Support for multilingual lyrics and templates

## Deploy On Render

This project is ready to deploy as a Render Web Service using `render.yaml`.

1. Push your latest code to GitHub.
2. In Render, click **New +** → **Blueprint**.
3. Connect your GitHub account and select this repository.
4. Render will read `render.yaml` and create the service automatically.
5. Wait for the first deploy to complete, then open the generated Render URL.

### Required Settings

- Runtime: Python 3.11 (already set in `render.yaml`)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

### Push Changes To GitHub

Use these commands after local updates:

```bash
git add -A
git commit -m "Describe your change"
git push origin main
```