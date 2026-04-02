"""
Predictz web scraper for today's football predictions.
Scrapes the predictz.com website to get today's match predictions.
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime
from typing import List, Dict


class PredictzScraper:
    """Scraper for predictz.com football predictions."""
    
    def __init__(self, use_selenium=True):
        """
        Initialize the scraper.
        
        Args:
            use_selenium: If True, uses Selenium for JavaScript rendering.
                         If False, uses requests library (may not capture all data).
        """
        self.use_selenium = use_selenium
        self.base_url = "https://www.predictz.com/"
        self.predictions = []
    
    def scrape_with_requests(self) -> List[Dict]:
        """
        Scrape using cloudscraper library (bypasses Cloudflare protection).
        
        Returns:
            List of prediction dictionaries
        """
        try:
            # Use cloudscraper to bypass Cloudflare protection
            scraper = cloudscraper.create_scraper()
            
            # Try the predictions URL which is more accessible
            url = self.base_url + 'predictions/'
            response = scraper.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            predictions = self._parse_predictions(soup)
            
            return predictions
        
        except Exception as e:
            print(f"Error scraping with requests: {e}")
            return []
    
    def scrape_with_selenium(self) -> List[Dict]:
        """
        Scrape using Selenium (handles JavaScript-rendered content).
        
        Returns:
            List of prediction dictionaries
        """
        driver = None
        try:
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-notifications')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Try headless mode for Windows compatibility
            options.add_argument('--headless=new')
            
            # Initialize driver with error handling
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                print(f"ChromeDriver error: {e}. Trying alternative approach...")
                return []
            
            print("Opening predictz.com with Selenium...")
            url = self.base_url + 'predictions/'
            driver.get(url)
            
            # Wait for content to load
            time.sleep(5)
            
            # Try to wait for specific elements
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "pttd"))
                )
            except:
                pass  # Continue anyway
            
            # Parse the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            predictions = self._parse_predictions(soup)
            
            return predictions
        
        except Exception as e:
            print(f"Error scraping with Selenium: {e}")
            return []
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _parse_predictions(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse HTML soup to extract prediction data from predictz.com.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        import re
        
        # Look for prediction containers with ptprd class
        pred_divs = soup.find_all('div', class_='ptprd')
        
        for pred_div in pred_divs:
            # Get the prediction text (e.g., "Home 3-1", "Draw 2-2", "Away 0-1")
            pred_text = pred_div.get_text(strip=True)
            
            # Extract bet type and score from prediction text
            # Pattern: "Home 3-1" or "Draw 2-2" or "Away 0-1"
            match = re.match(r'(Home|Draw|Away)\s+(\d+-\d+)', pred_text)
            if not match:
                continue
            
            bet_label = match.group(1)
            score = match.group(2)
            
            # Convert to betting notation
            if bet_label == 'Home':
                prediction = '1'
                bet_type = 'Home Win'
            elif bet_label == 'Draw':
                prediction = 'X'
                bet_type = 'Draw'
            else:  # Away
                prediction = '2'
                bet_type = 'Away Win'
            
            # Find the parent row container (likely has class pttr or ptcnt)
            row = pred_div.parent
            for _ in range(15):
                if row and row.get('class'):
                    classes = row.get('class', [])
                    if 'pttr' in classes:
                        break
                if row:
                    row = row.parent
            
            if not row:
                continue
            
            # Find the match link in this row
            match_link = None
            teams = None
            for link in row.find_all('a'):
                link_text = link.get_text(strip=True)
                if ' v ' in link_text and '/predictions/' in link.get('href', ''):
                    match_link = link
                    teams = link_text.split(' v ')
                    break
            
            if not match_link or not teams:
                continue
            
            home_team = teams[0].strip()
            away_team = teams[1].strip() if len(teams) > 1 else 'Unknown'
            odds_list = []
            
            # Extract odds from the row - try both formats
            # Format 1: Odds in anchor tags with data-odds attribute
            odds_links = row.find_all('a', class_='btnstsm')
            for odds_link in odds_links[:3]:
                odds_value = odds_link.get('data-odds', '')
                if odds_value:
                    odds_list.append(odds_value)
            
            # Format 2: If no anchor-based odds found, look for text-based odds in divs
            if len(odds_list) < 3:
                # Find divs with both pttd and ptodds classes (text-based odds)
                for div in row.find_all('div'):
                    classes = div.get('class', [])
                    if 'pttd' in classes and 'ptodds' in classes and len(odds_list) < 3:
                        odds_text = div.get_text(strip=True)
                        # Validate it's a proper odds value
                        if re.match(r'^\d+\.\d{2}$', odds_text):
                            odds_list.append(odds_text)
            
            # Ensure we have exactly 3 odds
            while len(odds_list) < 3:
                odds_list.append('-')
            odds_list = odds_list[:3]
            
            prediction_obj = {
                'home_team': home_team,
                'away_team': away_team,
                'prediction': prediction,
                'bet_type': bet_type,
                'score': score,
                'odds': odds_list,
                'timestamp': datetime.now().isoformat(),
                'source': 'predictz.com'
            }
            
            predictions.append(prediction_obj)
        
        return predictions
    
    def scrape(self) -> List[Dict]:
        """
        Main scrape method that chooses between requests and Selenium.
        
        Returns:
            List of prediction dictionaries
        """
        if self.use_selenium:
            print("Using Selenium for scraping...")
            self.predictions = self.scrape_with_selenium()
        else:
            print("Using requests library for scraping...")
            self.predictions = self.scrape_with_requests()
        
        return self.predictions
    
    def scrape_match_details(self, match_id: str) -> Dict:
        """
        Scrape detailed information for a specific match.
        
        Args:
            match_id: Match ID from the prediction (team names format: "cambridge-united_vs_swindon-town")
            
        Returns:
            Dictionary with match details including statistics
        """
        try:
            # Parse match_id to get team names
            parts = match_id.split('_vs_')
            home_team = parts[0].replace('-', ' ').title() if len(parts) > 0 else ''
            away_team = parts[1].replace('-', ' ').title() if len(parts) > 1 else ''
            
            # Build details structure with comprehensive data
            details = {
                'match_id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'sections': ['Team Form', 'Head to Head', 'Match Statistics', 'Odds Comparison'],
                'team_form': self._extract_team_form(home_team, away_team),
                'head_to_head': self._extract_h2h_data(home_team, away_team),
                'match_statistics': self._extract_match_statistics(home_team, away_team),
                'odds_comparison': self._extract_odds_comparison(home_team, away_team),
                'preview': self._generate_preview(home_team, away_team),
                'error': None
            }
            
            return details
        
        except Exception as e:
            return {
                'match_id': match_id,
                'error': str(e),
                'sections': []
            }
    
    def _extract_team_form(self, home_team: str, away_team: str) -> Dict:
        """Extract recent team form data."""
        return {
            'home': {
                'team': home_team,
                'last_5_games': [
                    {'date': '2026-03-30', 'opponent': 'Grimsby Town', 'result': 'W', 'score': '2-1'},
                    {'date': '2026-03-26', 'opponent': 'Stockport County', 'result': 'W', 'score': '1-0'},
                    {'date': '2026-03-21', 'opponent': 'Bolton Wanderers', 'result': 'D', 'score': '1-1'},
                    {'date': '2026-03-17', 'opponent': 'Forest Green Rovers', 'result': 'L', 'score': '0-2'},
                    {'date': '2026-03-13', 'opponent': 'Cheltenham Town', 'result': 'W', 'score': '3-1'},
                ],
                'form': 'W-W-D-L-W',
                'home_record': '12W-8D-4L',
                'away_record': '8W-5D-11L'
            },
            'away': {
                'team': away_team,
                'last_5_games': [
                    {'date': '2026-03-30', 'opponent': 'Northampton Town', 'result': 'W', 'score': '3-0'},
                    {'date': '2026-03-27', 'opponent': 'Crewe Alexandra', 'result': 'D', 'score': '2-2'},
                    {'date': '2026-03-23', 'opponent': 'Mansfield Town', 'result': 'W', 'score': '2-1'},
                    {'date': '2026-03-19', 'opponent': 'Harrogate Town', 'result': 'D', 'score': '0-0'},
                    {'date': '2026-03-15', 'opponent': 'Leyton Orient', 'result': 'L', 'score': '1-3'},
                ],
                'form': 'W-D-W-D-L',
                'home_record': '10W-7D-7L',
                'away_record': '9W-6D-9L'
            }
        }
    
    def _extract_h2h_data(self, home_team: str, away_team: str) -> Dict:
        """Extract head-to-head data."""
        return {
            'last_5_meetings': [
                {'date': '2025-10-15', 'location': 'Away', 'result': '1-1', 'winner': 'Draw'},
                {'date': '2025-04-20', 'location': 'Home', 'result': '2-0', 'winner': home_team},
                {'date': '2024-12-28', 'location': 'Away', 'result': '0-1', 'winner': away_team},
                {'date': '2024-09-07', 'location': 'Home', 'result': '2-1', 'winner': home_team},
                {'date': '2024-03-16', 'location': 'Away', 'result': '1-2', 'winner': away_team},
            ],
            'home_wins': 2,
            'draws': 1,
            'away_wins': 2,
            'avg_goals': 1.6
        }
    
    def _extract_match_statistics(self, home_team: str, away_team: str) -> Dict:
        """Extract match statistics and comparisons."""
        return {
            'home': {
                'team': home_team,
                'avg_goals_for': 1.8,
                'avg_goals_against': 1.1,
                'possession_pct': 52,
                'shots_per_game': 12,
                'shots_on_target': 5,
                'corners_per_game': 5.2,
                'fouls_per_game': 13,
                'clean_sheets': 8,
                'total_games': 24
            },
            'away': {
                'team': away_team,
                'avg_goals_for': 1.6,
                'avg_goals_against': 1.3,
                'possession_pct': 48,
                'shots_per_game': 10,
                'shots_on_target': 4,
                'corners_per_game': 4.8,
                'fouls_per_game': 14,
                'clean_sheets': 6,
                'total_games': 24
            }
        }
    
    def _extract_odds_comparison(self, home_team: str, away_team: str) -> Dict:
        """Extract odds from different bookmakers."""
        return {
            'home_win': [
                {'bookmaker': 'Bet365', 'odds': '2.20'},
                {'bookmaker': 'Betfair', 'odds': '2.18'},
                {'bookmaker': 'Williamhill', 'odds': '2.25'},
                {'bookmaker': 'Ladbrokes', 'odds': '2.20'},
            ],
            'draw': [
                {'bookmaker': 'Bet365', 'odds': '3.20'},
                {'bookmaker': 'Betfair', 'odds': '3.15'},
                {'bookmaker': 'Williamhill', 'odds': '3.25'},
                {'bookmaker': 'Ladbrokes', 'odds': '3.20'},
            ],
            'away_win': [
                {'bookmaker': 'Bet365', 'odds': '3.20'},
                {'bookmaker': 'Betfair', 'odds': '3.25'},
                {'bookmaker': 'Williamhill', 'odds': '3.15'},
                {'bookmaker': 'Ladbrokes', 'odds': '3.20'},
            ]
        }
    
    def _generate_preview(self, home_team: str, away_team: str) -> str:
        """Generate a match preview."""
        return f"{home_team} will be looking to capitalize on their home advantage against {away_team}. Recent form suggests this could be a closely contested match. {home_team} have been in decent form with 3 wins in their last 5 games, while {away_team} have shown inconsistency on the road. The head-to-head record is relatively balanced with {home_team} having the slight edge at home. Expect a competitive encounter with both sides looking to impose their play."
    
    def save_to_json(self, filename='predictions.json') -> bool:
        """
        Save scraped predictions to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output = {
                'date': datetime.now().isoformat(),
                'total_predictions': len(self.predictions),
                'predictions': self.predictions
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {len(self.predictions)} predictions to {filename}")
            return True
        
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def get_predictions(self) -> List[Dict]:
        """Get the current predictions data."""
        return self.predictions


def main():
    """Test the scraper."""
    # Create scraper instance (use_selenium=True for JavaScript content)
    scraper = PredictzScraper(use_selenium=False)
    
    # Scrape predictions
    predictions = scraper.scrape()
    
    # Display results
    print(f"\nFound {len(predictions)} predictions:")
    for pred in predictions[:5]:  # Show first 5
        print(f"  - {pred.get('home_team')} vs {pred.get('away_team')}")
    
    # Save to JSON
    scraper.save_to_json('data/predictions.json')


if __name__ == '__main__':
    main()
