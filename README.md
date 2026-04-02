# Predictz Scraper

A Python Flask web application that scrapes today's football predictions from [predictz.com](https://predictz.com).

## Features

- 🌐 **Web Interface**: Clean, modern UI for viewing predictions
- 🔄 **Multiple Scraping Methods**: Choose between fast (requests) and complete (Selenium) scraping
- 📊 **JSON Export**: Automatically saves predictions to JSON format
- 🎯 **Real-time Status**: Monitor scraping progress in real-time
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🚀 **Background Processing**: Scraping runs without blocking the UI

## Project Structure

```
gool/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── scrapers/
│   └── predictz_scraper.py    # Web scraping logic
├── templates/
│   └── index.html             # Web UI
├── static/
│   ├── style.css              # Styling
│   └── script.js              # Frontend logic
├── data/
│   └── predictions.json       # Scraped data (auto-generated)
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone/Navigate to the project**:
   ```bash
   cd gool
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download ChromeDriver** (required for Selenium method):
   - The `webdriver-manager` package in requirements.txt will automatically handle this.

## Usage

### Running the Web App

```bash
python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Using the Web Interface

1. **Select Scraping Method**:
   - **Fast (Requests)**: Uses the `requests` library, faster but may miss JavaScript-rendered content
   - **Complete (Selenium)**: Uses Selenium with a real browser, slower but captures all content

2. **Click "Scrape Predictions"**:
   - The scraper runs in the background
   - Status updates in real-time
   - Results display as cards in the main area

3. **View Raw JSON**:
   - Expand the "Raw JSON Data" section
   - Click "Download JSON" to save the predictions

### API Endpoints

#### Get Predictions
```bash
GET /api/predictions
```
Returns all scraped predictions.

#### Get Limited Predictions
```bash
GET /api/predictions/<limit>
```
Returns first `<limit>` predictions.

#### Start Scraping
```bash
POST /api/scrape?method=requests
# or
POST /api/scrape?method=selenium
```
Starts scraping in background. Returns 202 (Accepted) if successful.

#### Get Status
```bash
GET /api/status
```
Returns scraping status and timestamp of last scrape.

### Command-line Usage

You can also use the scraper directly from command line:

```bash
python -c "from scrapers.predictz_scraper import PredictzScraper; \
scraper = PredictzScraper(use_selenium=False); \
scraper.scrape(); \
scraper.save_to_json('data/predictions.json')"
```

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for web scraping (fast method)
- **beautifulsoup4**: HTML/XML parsing
- **selenium**: Browser automation (complete method)
- **webdriver-manager**: Automatic ChromeDriver management
- **python-dotenv**: Environment variable management
- **lxml**: XML/HTML parsing library

## Advanced: How the Scraper Works

### Method 1: Fast Scraping (Requests)
1. Sends HTTP GET request to predictz.com
2. Parses HTML with BeautifulSoup
3. Extracts prediction data using CSS selectors
4. Faster but may miss dynamically loaded content

### Method 2: Complete Scraping (Selenium)
1. Opens a Chrome browser instance
2. Navigates to predictz.com
3. Waits for JavaScript to render content
4. Parses the fully-loaded webpage
5. Closes browser and returns data
6. Slower but captures all content

### Data Structure

Each prediction is stored as:
```json
{
  "home_team": "Team A",
  "away_team": "Team B",
  "prediction": "1-1",
  "timestamp": "2024-04-02T14:30:00",
  "source": "predictz.com"
}
```

## Customization

### Changing the Scraping URL

Edit [app.py](app.py) and modify the `base_url`:
```python
self.base_url = "https://www.predictz.com/predictions/"
```

### Adjusting HTML Selectors

Edit [scrapers/predictz_scraper.py](scrapers/predictz_scraper.py#L89) and update the selectors:
```python
match_elements = soup.find_all(['div', 'tr'], class_=lambda x: x and 'match' in x.lower())
```

### Styling

All CSS is in [static/style.css](static/style.css). Modify colors, fonts, and layout there.

## Troubleshooting

### Chrome/ChromeDriver Issues
- Make sure Chrome browser is installed
- `webdriver-manager` will auto-download the correct ChromeDriver
- If issues persist, manually download from [chromedriver.chromium.org](https://chromedriver.chromium.org)

### No Predictions Found
- The website structure may have changed
- Check the HTML selectors in `predictz_scraper.py`
- Open browser DevTools (F12) to inspect the page structure
- Update the selectors accordingly

### Port Already in Use
If port 5000 is in use, edit [app.py](app.py#L95):
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change 5001 to desired port
```

### Selenium Hangs
- Ensure Chrome is installed
- Try the Fast method (Requests) instead
- Increase timeout in `predictz_scraper.py` line 71

## Learning Resources

This project demonstrates advanced web scraping techniques:

1. **BeautifulSoup Parsing**: HTML/XML parsing and data extraction
2. **Selenium Automation**: Browser automation and JavaScript handling
3. **Flask Web Framework**: Building REST APIs and web applications
4. **Async Operations**: Background threading for non-blocking scraping
5. **Responsive Web Design**: Mobile-friendly UI with CSS Grid/Flexbox
6. **API Design**: RESTful endpoints for data access

## Legal Notice

Web scraping should be done responsibly:
- Always check the website's `robots.txt` and Terms of Service
- Don't overload servers with too many requests
- Add delays between requests if scraping multiple pages
- Consider using official APIs when available
- Respect copyright and data ownership

## Future Improvements

- [ ] Database storage instead of JSON
- [ ] Scheduled auto-scraping
- [ ] Data visualization and statistics
- [ ] Multiple sports/leagues support
- [ ] Email notifications for matches
- [ ] Docker containerization
- [ ] Unit tests and CI/CD

## 🚀 Deployment Guide

### Deploy on Railway.app (Recommended)

1. Create account at [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account and select this repository
5. Railway auto-detects Flask and deploys automatically
6. Get a public URL (e.g., `https://your-app.railway.app`)

### Deploy on Render

1. Go to [render.com](https://render.com)
2. Click "New +"
3. Select "Web Service"
4. Connect GitHub and select repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `gunicorn app:app`
7. Click Deploy

### Deploy on Heroku (Paid)

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Open app
heroku open
```

### Environment Variables

Create these in your deployment platform settings:
- `DEBUG=False`
- `HOST=0.0.0.0`
- `PORT=5000`

## License

MIT License - Feel free to use for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Inspect the browser console for errors
3. Review the server logs in terminal
4. Check the HTML structure of predictz.com

---

**Happy Scraping!** ⚽
