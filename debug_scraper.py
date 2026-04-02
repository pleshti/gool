#!/usr/bin/env python3
"""Debug script to see what content we're scraping"""

import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()
url = 'https://www.predictz.com/predictions/'

print("Fetching page...")
response = scraper.get(url, timeout=15)
content = response.text

# Save the content to a file for inspection
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Page fetched. Content length: {len(content)} bytes")
print("Saved to debug_page.html")

# Parse and check for match patterns
soup = BeautifulSoup(content, 'html.parser')

# Look for all links containing " v "
all_links = soup.find_all('a')
print(f"\nTotal links found: {len(all_links)}")

matches_found = 0
for link in all_links:
    text = link.get_text(strip=True)
    if ' v ' in text:
        matches_found += 1
        if matches_found <= 10:
            print(f"Match found: {text}")
            # Check parent text for prediction info
            parent = link.parent
            if parent:
                parent_text = parent.get_text(strip=True)[:100]
                print(f"  Parent text: {parent_text}")

print(f"\nTotal matches with ' v ': {matches_found}")

# Also look for any divs or spans with "prediction" in class
prediction_elements = soup.find_all(['div', 'span'], class_=lambda x: x and 'prediction' in str(x).lower())
print(f"Elements with 'prediction' in class: {len(prediction_elements)}")

# Look for key words
text = soup.get_text().lower()
print(f"\n'wigan' found: {'wigan' in text}")
print(f"'las palmas' found: {'las palmas' in text}")
print(f"'prediction' found: {'prediction' in text}")
