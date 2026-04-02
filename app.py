"""
Flask web app for scraping predictz.com football predictions.
Provides a web interface and API endpoints for predictions.
"""

from flask import Flask, render_template, jsonify, request
import json
import osfrom dotenv import load_dotenv

load_dotenv()from datetime import datetime
from scrapers.predictz_scraper import PredictzScraper
import threading

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global scraper instance
scraper = None
is_scraping = False
last_scrape_time = None


def get_predictions_from_file():
    """Load predictions from JSON file."""
    try:
        if os.path.exists('data/predictions.json'):
            with open('data/predictions.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading predictions file: {e}")
    
    return {'predictions': [], 'total_predictions': 0, 'date': None}


def scrape_in_background(use_selenium=False):
    """Run scraper in background thread."""
    global is_scraping, last_scrape_time, scraper
    
    try:
        is_scraping = True
        print("Starting scrape...")
        
        scraper = PredictzScraper(use_selenium=use_selenium)
        scraper.scrape()
        scraper.save_to_json('data/predictions.json')
        
        last_scrape_time = datetime.now().isoformat()
        print("Scrape completed successfully")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        is_scraping = False


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """API endpoint to get current predictions."""
    data = get_predictions_from_file()
    return jsonify(data), 200


@app.route('/api/scrape', methods=['POST'])
def scrape_predictions():
    """
    API endpoint to trigger scraping.
    
    Query params:
        - method: 'requests' or 'selenium' (default: 'requests')
    """
    global is_scraping
    
    if is_scraping:
        return jsonify({'error': 'Scraping already in progress'}), 409
    
    method = request.args.get('method', 'requests').lower()
    use_selenium = method == 'selenium'
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_in_background, args=(use_selenium,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Scraping started',
        'method': method,
        'status': 'in_progress'
    }), 202


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get scraping status."""
    return jsonify({
        'is_scraping': is_scraping,
        'last_scrape_time': last_scrape_time,
        'data_available': os.path.exists('data/predictions.json')
    }), 200


@app.route('/api/predictions/<int:limit>', methods=['GET'])
def get_predictions_limit(limit):
    """Get limited number of predictions."""
    data = get_predictions_from_file()
    predictions = data.get('predictions', [])[:limit]
    
    return jsonify({
        'predictions': predictions,
        'total_returned': len(predictions),
        'total_available': data.get('total_predictions', 0)
    }), 200


@app.route('/api/match-details/<match_id>', methods=['GET'])
def get_match_details(match_id):
    """Get detailed information for a specific match."""
    from scrapers.predictz_scraper import PredictzScraper
    
    scraper = PredictzScraper(use_selenium=False)
    details = scraper.scrape_match_details(match_id)
    
    return jsonify(details), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run Flask app
    # Use 0.0.0.0 for deployment, 127.0.0.1 for local development
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)
