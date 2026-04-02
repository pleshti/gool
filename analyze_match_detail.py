"""
Analyze match detail page structure to extract statistics
"""

import cloudscraper
from bs4 import BeautifulSoup

def analyze_match_page():
    """Analyze the HTML structure of a match detail page"""
    
    # Try a real match from today's predictions
    match_id = "cambridge-united-swindon-town"
    detail_url = f"https://www.predictz.com/predictions//{match_id}/"
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(detail_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Save the page to file for inspection
        with open('match_detail_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("Page saved to match_detail_page.html")
        
        # Look for divs and sections
        print("\n=== Looking for data containers ===")
        
        # Look for any divs with "form" or "statistics" in class/id
        for div in soup.find_all('div', limit=50):
            classes = div.get('class', [])
            div_id = div.get('id', '')
            if any(word in str(classes + [div_id]).lower() for word in ['form', 'stat', 'h2h', 'head', 'lineup', 'squad', 'news']):
                print(f"Found: class={classes} id={div_id}")
        
        # Look for tables (potential stats)
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")
        for i, table in enumerate(tables[:3]):
            print(f"\nTable {i}:")
            rows = table.find_all('tr')
            for row in rows[:3]:
                cells = row.find_all('td') or row.find_all('th')
                print("  ", [cell.get_text(strip=True)[:30] for cell in cells])
        
        # Look for sections with team names
        print("\n=== Looking for team data ===")
        page_text = soup.get_text()
        
        # Find team-related content
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['cambridge', 'swindon', 'form', 'statistics', 'h2h']):
                print(f"{i}: {line.strip()[:100]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    analyze_match_page()
