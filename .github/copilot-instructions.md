# Predictz Scraper - Project Instructions

## Project Overview

This is a Python Flask web application that scrapes football predictions from predictz.com. It includes a modern web UI, multiple scraping methods (requests and Selenium), and JSON export capabilities.

## Technology Stack

- **Backend**: Python 3.8+, Flask 2.3
- **Scraping**: BeautifulSoup4, Selenium, Requests
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Format**: JSON
- **Browser Automation**: Selenium with ChromeDriver

## Project Structure

```
gool/
├── app.py                      # Flask application and API endpoints
├── requirements.txt            # Python dependencies
├── scrapers/
│   └── predictz_scraper.py    # Core scraping logic with 2 methods
├── templates/
│   └── index.html             # Web UI template
├── static/
│   ├── style.css              # Responsive styling
│   └── script.js              # Frontend interaction logic
├── data/                       # (auto-created) JSON storage
└── README.md                   # Comprehensive documentation
```

## Key Features

1. **Two Scraping Methods**:
   - Fast: Using requests + BeautifulSoup
   - Complete: Using Selenium + browser automation

2. **Web Interface**:
   - Real-time status monitoring
   - Prediction cards display
   - JSON viewer and download
   - Responsive design (mobile-friendly)

3. **Background Processing**:
   - Scraping runs in background threads
   - Non-blocking UI
   - Real-time status updates

4. **REST API**:
   - GET /api/predictions
   - POST /api/scrape
   - GET /api/status
   - GET /api/predictions/<limit>

## Development Guidelines

### Adding New Features
1. Update `scrapers/predictz_scraper.py` for scraping logic
2. Add API endpoints in `app.py`
3. Update UI in `templates/index.html` and `static/script.js`
4. Update `README.md` with new features

### Debugging
- Check browser console for frontend errors (F12)
- Check terminal for Flask/backend errors
- Use browser DevTools to inspect HTML structure
- Set Flask `debug=True` for auto-reload

### Best Practices
- Always use try-except for scraping operations
- Test with both scraping methods
- Validate user input from API
- Add proper error handling
- Keep CSS responsive for all screen sizes

## Installation & Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open browser: `http://127.0.0.1:5000`

## Testing Scrapers

To test scraping without the web interface:

```bash
python scrapers/predictz_scraper.py
```

This will scrape and save to `data/predictions.json`.

## Common Customizations

1. **Change scraping target**: Edit `base_url` in `PredictzScraper` class
2. **Modify HTML selectors**: Update `_parse_predictions()` method
3. **Change UI colors**: Edit CSS variables in `static/style.css`
4. **Add more API endpoints**: Add methods in `app.py`

## Dependencies Overview

- `Flask`: Web framework for UI and API
- `requests`: HTTP library for fast scraping
- `beautifulsoup4`: HTML parsing
- `selenium`: Browser automation
- `webdriver-manager`: Auto-manages ChromeDriver downloads
- `lxml`: XML/HTML parsing library

## Performance Notes

- Requests method: ~2-5 seconds per scrape
- Selenium method: ~5-15 seconds per scrape
- JSON stored in `data/` folder
- Predictions can be filtered with `/api/predictions/<limit>`

## Next Steps for Enhancement

1. Add database (SQLite/PostgreSQL) instead of JSON
2. Implement scheduled scraping (cron jobs)
3. Add data visualization/charts
4. Support additional sports/leagues
5. Add user authentication
6. Deploy to cloud (Heroku, AWS, etc.)

---

Made with ⚽ for learning advanced web scraping techniques.
