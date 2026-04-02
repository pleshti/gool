"""
Firebase Realtime Database service module for storing and retrieving predictions.
"""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os
import json
from typing import Dict, List, Optional

# Initialize Firebase
_database = None
_RTDB_URL = 'https://hugingbearer-default-rtdb.europe-west1.firebasedatabase.app'


def _firebase_credentials():
    """Local JSON key if present; otherwise Application Default Credentials (Cloud Functions, etc.)."""
    env_path = (os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or '').strip()
    if env_path and os.path.isfile(env_path):
        return credentials.Certificate(env_path)
    if os.path.isfile('serviceAccountKey.json'):
        return credentials.Certificate('serviceAccountKey.json')
    return credentials.ApplicationDefault()


def initialize_realtime_db():
    """Initialize Firebase Realtime Database (JSON key locally, ADC on Google Cloud)."""
    global _database
    
    if _database is not None:
        return _database
    
    try:
        # Initialize Firebase app if not already done
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = _firebase_credentials()
            firebase_admin.initialize_app(cred, {'databaseURL': _RTDB_URL})
        
        _database = db.reference()
        print("[OK] Realtime Database initialized successfully")
        return _database
    
    except Exception as e:
        print(f"[ERROR] Error initializing Realtime Database: {e}")
        return None


def store_predictions(predictions_dict: Dict) -> Optional[str]:
    """
    Store predictions in Firebase Realtime Database.
    
    Args:
        predictions_dict: Dictionary with 'date', 'total_predictions', 'predictions'
        
    Returns:
        Reference path if successful, None if failed
    """
    database = initialize_realtime_db()
    if database is None:
        return None
    
    try:
        # Prepare data with timestamp
        timestamp = datetime.now().isoformat()
        data = {
            'timestamp': timestamp,
            'date': predictions_dict.get('date'),
            'total_predictions': predictions_dict.get('total_predictions', 0),
            'predictions': predictions_dict.get('predictions', []),
            'source': 'predictz.com'
        }
        
        # Store in /predictions/latest
        predictions_ref = database.child('predictions').child('latest')
        predictions_ref.set(data)
        
        # Also store timestamped copy for history
        timestamp_key = timestamp.replace(':', '-').replace('.', '-')
        history_ref = database.child('predictions').child('history').child(timestamp_key)
        history_ref.set(data)
        
        print(f"[OK] Predictions stored in Realtime Database")
        return 'latest'
    
    except Exception as e:
        print(f"[ERROR] Error storing predictions to Realtime Database: {e}")
        return None


def get_latest_predictions() -> Optional[Dict]:
    """
    Get the latest predictions from Firebase Realtime Database.
    
    Returns:
        Latest prediction document
    """
    database = initialize_realtime_db()
    if database is None:
        return None
    
    try:
        predictions_ref = database.child('predictions').child('latest')
        data = predictions_ref.get()
        
        # Handle both snapshot and direct dict returns
        if hasattr(data, 'val'):
            # It's a DataSnapshot
            value = data.val()
        else:
            # It's already a dict
            value = data
        
        if value:
            result = value if isinstance(value, dict) else {'error': 'Unexpected data format'}
            # Add a reference marker
            result['ref'] = 'latest'
            return result
        else:
            return None
    
    except Exception as e:
        print(f"[ERROR] Error retrieving predictions from Realtime Database: {e}")
        return None


def get_prediction_history(limit: int = 10) -> Optional[List[Dict]]:
    """
    Get prediction history from Firebase Realtime Database.
    
    Args:
        limit: Number of recent scrapes to retrieve (newest first)
        
    Returns:
        List of historical prediction documents
    """
    database = initialize_realtime_db()
    if database is None:
        return None
    
    try:
        history_ref = database.child('predictions').child('history')
        data = history_ref.order_by_child('timestamp').limit_to_last(limit).get()
        
        # Handle both snapshot and direct dict returns
        if hasattr(data, 'val'):
            # It's a DataSnapshot
            value = data.val()
        else:
            # It's already a dict
            value = data
        
        if value and isinstance(value, dict):
            # Convert to list and reverse to get newest first
            results = []
            for key, doc_value in sorted(value.items(), reverse=True):
                if isinstance(doc_value, dict):
                    doc_value['ref'] = key
                    results.append(doc_value)
            return results[:limit] if results else None
        else:
            return None
    
    except Exception as e:
        print(f"[ERROR] Error retrieving prediction history: {e}")
        return None


def sync_json_to_realtime_db(json_file_path: str) -> Optional[str]:
    """
    Sync existing JSON predictions to Realtime Database (useful for backfill).
    
    Args:
        json_file_path: Path to predictions.json
        
    Returns:
        Reference if successful, None if failed
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return store_predictions(data)
    
    except Exception as e:
        print(f"[ERROR] Error syncing JSON to Realtime Database: {e}")
        return None
