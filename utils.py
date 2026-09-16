import os
import pdfkit
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

WKHTMLTOPDF_ENV = os.environ.get("WKHTMLTOPDF_PATH", None)

def get_wkhtmltopdf_config():
    paths_to_try = []
    if WKHTMLTOPDF_ENV:
        paths_to_try.append(WKHTMLTOPDF_ENV)
    paths_to_try += [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        "/usr/local/bin/wkhtmltopdf",
        "/usr/bin/wkhtmltopdf",
        "/opt/homebrew/bin/wkhtmltopdf",
        "/opt/local/bin/wkhtmltopdf"
    ]
    for p in paths_to_try:
        if p and os.path.exists(p):
            try:
                return pdfkit.configuration(wkhtmltopdf=p)
            except Exception:
                continue
    return None

PDFKIT_CONFIG = get_wkhtmltopdf_config()