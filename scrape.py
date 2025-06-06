import os
import re
from bs4 import BeautifulSoup
import requests
from crawl import get_subpages, BASE_URL


DATA_DIR = "documents"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_text(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find all elements with class "tab"
        tab_elements = soup.find_all(class_="tab")
        if not tab_elements:
            print(f"No .tab elements found in {url}")
            return None
        # Extract text from each .tab element
        text = "\n\n".join(tab.get_text(separator="\n", strip=True) for tab in tab_elements)
        return text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def sanitize_filename(url):
    filename = re.sub(r'[^a-zA-Z0-9]', '_', url)
    return filename[:100]  # Limit filename length

def main():
    urls = get_subpages(BASE_URL)
    for url in urls:
        text = fetch_text(url)
        if text:
            filename = sanitize_filename(url) + ".txt"
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Saved: {filepath}")


if __name__ == "__main__":
    main()
