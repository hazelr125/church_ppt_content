import urllib.request
import os

url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf"
dest = "NotoSansKannada-Regular.ttf"

try:
    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Successfully downloaded to {os.path.abspath(dest)}")
except Exception as e:
    print(f"Error downloading font: {e}")
