#!/usr/bin/env python3
"""Test script for the predictz scraper"""

from scrapers.predictz_scraper import PredictzScraper

# Test with requests method (now improved)
print("Testing scraper with requests method (improved)...")
scraper = PredictzScraper(use_selenium=False)
predictions = scraper.scrape()

print(f"\nFound {len(predictions)} predictions!")
print("\nFirst 10 predictions:")
for i, pred in enumerate(predictions[:10], 1):
    bet_type = pred.get('bet_type', 'N/A')
    print(f"{i}. {pred['home_team']} vs {pred['away_team']} - {pred['prediction']} (Bet: {bet_type})")

# Save to JSON
scraper.save_to_json('data/predictions.json')
print("\nPredictions saved to data/predictions.json")
