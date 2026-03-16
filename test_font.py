import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

try:
    font_path = 'C:\\Windows\\Fonts\\Nirmala.ttc'
    pdfmetrics.registerFont(TTFont('Kannada', font_path, subfontIndex=0))
    print("Success")
except Exception as e:
    print("Error:", e)
