import requests
from bs4 import BeautifulSoup
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SEED_URL = "https://example.com"
MAX_PAGES = 5

headers = {
    "User-Agent": "Mozilla/5.0"
}

queue = [SEED_URL]
visited = set()

documents = {}
graph = {}

doc_id = 0

while queue and len(visited) < MAX_PAGES:
    url = queue.pop(0)

    if url in visited:
        continue

    print(f"\nCrawling: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)

        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text
        text = soup.get_text()
        documents[str(doc_id)] = text

        # Extract links
        links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and href.startswith("http"):
                links.append(href)

                if href not in visited:
                    queue.append(href)

        graph[str(doc_id)] = links

        visited.add(url)
        doc_id += 1

    except Exception as e:
        print("Error:", e)

# Save data
with open("documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2)

with open("graph.json", "w", encoding="utf-8") as f:
    json.dump(graph, f, indent=2)

print("\nCrawling completed!")