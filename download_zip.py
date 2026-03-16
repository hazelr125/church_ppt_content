import urllib.request
import zipfile
import os

url = "https://fonts.google.com/download?family=Noto%20Sans%20Kannada"
zip_path = "NotoSansKannada.zip"
extract_dir = "fonts"

print("Downloading font zip...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
    out_file.write(response.read())

print("Extracting...")
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print("Done. Files extracted to fonts/:")
for f in os.listdir(extract_dir):
    print(" -", f)
