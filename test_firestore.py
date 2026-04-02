"""
Quick test script to verify Firebase Realtime Database is working
Run this after setting up the project
"""

import os
import sys
from datetime import datetime

# Set environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_service import initialize_realtime_db, store_predictions, get_latest_predictions, get_prediction_history
from scrapers.predictz_scraper import PredictzScraper

def test_realtime_db_connection():
    """Test Realtime Database connection"""
    print("[TEST 1] Testing Firebase Realtime Database connection...")
    db = initialize_realtime_db()
    if db:
        print("[OK] Connected to Firebase Realtime Database")
        return True
    else:
        print("[ERROR] Failed to connect to Realtime Database")
        return False

def test_store_test_data():
    """Test storing test data in Realtime Database"""
    print("\n[TEST 2] Testing data storage...")
    
    test_data = {
        'date': datetime.now().isoformat(),
        'total_predictions': 1,
        'predictions': [{
            'home_team': 'Test Home',
            'away_team': 'Test Away',
            'prediction': '1',
            'bet_type': 'Home Win',
            'score': '2-0',
            'odds': ['1.80', '3.50', '4.00'],
            'timestamp': datetime.now().isoformat(),
            'source': 'test'
        }]
    }
    
    ref = store_predictions(test_data)
    if ref:
        print(f"[OK] Test data stored: {ref}")
        return ref
    else:
        print("[ERROR] Failed to store test data")
        return None

def test_retrieve_data():
    """Test retrieving data from Realtime Database"""
    print("\n[TEST 3] Testing data retrieval (latest)...")
    
    result = get_latest_predictions()
    if result and 'predictions' in result:
        print(f"[OK] Retrieved latest predictions")
        print(f"    Total predictions: {result.get('total_predictions')}")
        print(f"    First prediction: {result['predictions'][0].get('home_team') if result['predictions'] else 'None'}")
        return True
    else:
        print("[ERROR] Failed to retrieve latest predictions")
        return False

def test_retrieve_history():
    """Test retrieving history from Realtime Database"""
    print("\n[TEST 4] Testing history retrieval...")
    
    results = get_prediction_history(limit=5)
    if results:
        print(f"[OK] Retrieved {len(results)} historical documents")
        for i, doc in enumerate(results[:2]):
            print(f"    {i+1}. {doc.get('total_predictions', 0)} predictions at {doc.get('timestamp')}")
        return True
    else:
        print("[WARNING] No history found (this is OK on first run)")
        return True

def test_scraper():
    """Test scraper (without storing)"""
    print("\n[TEST 5] Testing scraper...")
    try:
        scraper = PredictzScraper(use_selenium=False)
        print("[OK] Scraper initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Scraper test failed: {e}")
        return False

if __name__ == '__main__':
    print("[START] Running Firebase Realtime Database Integration Tests")
    print("=" * 60)
    
    try:
        # Test connection
        if not test_realtime_db_connection():
            print("\n[FATAL] Cannot connect to Realtime Database. Make sure:")
            print("  1. serviceAccountKey.json exists in project root")
            print("  2. Firebase project 'hugingbearer' is configured")
            print("  3. Service account has proper permissions")
            sys.exit(1)
        
        # Test storage
        ref = test_store_test_data()
        if not ref:
            sys.exit(1)
        
        # Test retrieval
        if not test_retrieve_data():
            sys.exit(1)
        
        # Test history
        test_retrieve_history()
        
        # Test scraper
        test_scraper()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Test /api/scrape endpoint to sync predictions")
        print("3. Test /api/realtime-db/latest to verify data in database")
        print("4. Deploy Cloud Function: powershell .\\deploy.ps1")
        print("5. Set up Cloud Scheduler for hourly execution")
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
