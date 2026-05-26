import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://example.com" 

try:
    response = requests.get(url, verify=False, timeout=5)

    if response.status_code == 200:
        print("Status Code:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            print("Title:", soup.title.text)
        else:
            print("No title found")

        links = []

        for a in soup.find_all("a"):
            href = a.get("href")
            if href:
                links.append(href)

        links = list(set(links))

        print("\nFirst 10 Links:")
        for link in links[:10]:
            print(link)

    else:
        print("Failed with status code:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Error occurred:", e)




if response.status_code == 200:
    print("Request successful")
else:
    print("Failed to fetch page") 