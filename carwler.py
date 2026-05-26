import requests
import urllib3

# disable warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://example.com"

response = requests.get(url, verify=False)

print(response.status_code)
print(response.text[:200])