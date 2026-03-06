```python
import requests
from bs4 import BeautifulSoup
import time

url = "https://example.com"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

try:
    with requests.Session() as session:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.find('div', class_='target-class')
        if element:
            print(element.get_text())
        else:
            print("Target element not found")
except Exception as e:
    print(f"Error: {e}")

time.sleep(2)
```