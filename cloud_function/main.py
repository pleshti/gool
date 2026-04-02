"""
Google Cloud Function for hourly prediction scraping.
Triggered by Cloud Scheduler.
Stores predictions in Firebase Realtime Database.
"""

import functions_framework
from datetime import datetime

from scrapers.predictz_scraper import PredictzScraper

try:
    from firebase_service import store_predictions
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False
    print("[WARNING] Firebase service not available")


@functions_framework.http
def scrape_predictions(request):
    """
    HTTP Cloud Function to scrape predictions and store in Firebase Realtime Database.
    Triggered hourly by Cloud Scheduler.
    
    Args:
        request: Cloud Functions request object
        
    Returns:
        JSON response with status
    """
    try:
        print("[SCRAPING] Starting hourly scrape...")
        
        # Run scraper with requests method (faster for Cloud Functions)
        scraper = PredictzScraper(use_selenium=False)
        scraper.scrape()
        
        # Prepare data
        predictions_data = {
            'date': datetime.now().isoformat(),
            'total_predictions': len(scraper.predictions),
            'predictions': scraper.predictions
        }
        
        # Store in Realtime Database
        if FIREBASE_ENABLED:
            ref = store_predictions(predictions_data)
            if ref:
                print(f"[SUCCESS] Scrape completed and stored in Realtime Database: {ref}")
                return {
                    'status': 'success',
                    'message': 'Predictions scraped and stored',
                    'total_predictions': len(scraper.predictions),
                    'ref': ref,
                    'timestamp': predictions_data['date']
                }, 200
            else:
                return {
                    'status': 'partial_success',
                    'message': 'Scraped but Realtime Database storage failed',
                    'total_predictions': len(scraper.predictions),
                    'timestamp': predictions_data['date']
                }, 206
        else:
            return {
                'status': 'error',
                'message': 'Firebase not configured'
            }, 500
    
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {
            'status': 'error',
            'message': error_msg
        }, 500
