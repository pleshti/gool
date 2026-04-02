#!/usr/bin/env python3
"""Analyze match detail page to see what data is available."""

from bs4 import BeautifulSoup
import cloudscraper

# Create a scraper to bypass Cloudflare
scraper = cloudscraper.create_scraper()

# Try to fetch a match detail page
match_url = "https://www.predictz.com/predictions/england/league-one/1147858/"

try:
    response = scraper.get(match_url, timeout=10)
    response.raise_for_status()
    print(f"Status: {response.status_code}")
    print(f"Page length: {len(response.text)} characters\n")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Look for key sections
    print("=== Match Detail Page Analysis ===\n")
    
    # Find main heading
    h1 = soup.find('h1')
    if h1:
        print(f"Title: {h1.get_text(strip=True)}\n")
    
    # Find text with specific keywords
    page_text = soup.get_text()
    
    print("Available Data Sections:")
    if 'H2H' in page_text or 'head' in page_text.lower():
        print("  - Head-to-Head/Match History")
    if 'Form' in page_text or 'form' in page_text.lower():
        print("  - Team Form/Recent Results")
    if 'Statistics' in page_text or 'statistics' in page_text.lower():
        print("  - Match Statistics")
    if 'Injury' in page_text or 'injury' in page_text.lower():
        print("  - Injury/Absence Info")
    if 'Team News' in page_text or 'team news' in page_text.lower():
        print("  - Team News/Lineups")
    if '%' in page_text:
        print("  - Percentage/Probability Data")
    if 'Prediction' in page_text:
        print("  - Prediction Analysis")
        
    # Look for data in specific containers
    print("\n=== Key HTML Elements ===")
    
    # Looking for tables which often contain statistics
    tables = soup.find_all('table', limit=10)
    print(f"Tables found: {len(tables)}")
    
    # Looking for stats blocks
    stats_divs = soup.find_all('div', class_=lambda x: x and 'stat' in str(x).lower(), limit=10)
    print(f"Statistics divs found: {len(stats_divs)}")
    
    # Looking for prediction info
    pred_divs = soup.find_all('div', class_=lambda x: x and 'pred' in str(x).lower(), limit=10)
    print(f"Prediction divs found: {len(pred_divs)}")
    
    # Save first 5000 chars for inspection
    print("\n=== Saving sample HTML for inspection ===")
    with open('sample_detail_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text[:10000])
    print("Saved first 10,000 characters to sample_detail_page.html")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
