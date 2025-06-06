import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


BASE_URL = "https://www.angelone.in/support"

def get_subpages(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(url, href)
        # Only include links within the same domain and under /support/
        parsed = urlparse(full_url)
        if parsed.netloc == urlparse(BASE_URL).netloc and parsed.path.startswith("/support/"):
            links.add(full_url)
    return sorted(links)

if __name__ == "__main__":
    subpage_urls = get_subpages(BASE_URL)
    for page_url in subpage_urls:
        print(page_url)
