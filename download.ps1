[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Write-Host "Downloading NotoSansKannada..."
Invoke-WebRequest -Uri "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf" -OutFile "NotoSansKannada-Regular.ttf"
Write-Host "Download complete!"
