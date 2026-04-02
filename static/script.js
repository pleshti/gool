/**
 * Predictz Scraper - Frontend JavaScript
 */

// DOM Elements
const scrapeBtn = document.getElementById('scrapeBtn');
const methodSelect = document.getElementById('method');
const statusBadge = document.getElementById('status');
const lastScrapeEl = document.getElementById('lastScrape');
const predictionCountEl = document.getElementById('predictionCount');
const loadingSpinner = document.getElementById('loadingSpinner');
const noPredictions = document.getElementById('noPredictions');
const predictionsList = document.getElementById('predictionsList');
const jsonData = document.getElementById('jsonData');
const jsonHeader = document.querySelector('.json-header');
let isScrapingGlobal = false;

// Event Listeners
scrapeBtn.addEventListener('click', startScraping);
jsonHeader.addEventListener('click', toggleJson);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPredictions();
    checkStatus();
    // Check status every 2 seconds while scraping
    setInterval(checkStatus, 2000);
});

/**
 * Start scraping process
 */
async function startScraping() {
    if (isScrapingGlobal) return;

    const method = methodSelect.value;

    try {
        isScrapingGlobal = true;
        updateUI('scraping');
        showLoading(true);
        
        const response = await fetch(`/api/scrape?method=${method}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 202) {
            console.log('Scraping started in background');
            // Poll for completion
            pollForCompletion();
        } else if (response.status === 409) {
            updateUI('error');
            alert('Scraping is already in progress');
        } else {
            updateUI('error');
            alert('Failed to start scraping');
        }
    } catch (error) {
        console.error('Error:', error);
        updateUI('error');
        showLoading(false);
        alert('Error starting scraping: ' + error.message);
    }
}

/**
 * Poll for scraping completion
 */
function pollForCompletion() {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (!data.is_scraping) {
                clearInterval(pollInterval);
                console.log('Scraping completed');
                
                // Load new predictions
                await loadPredictions();
                updateUI('ready');
                showLoading(false);
                isScrapingGlobal = false;
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }, 1000);
}

/**
 * Check and display current status
 */
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.last_scrape_time) {
            lastScrapeEl.textContent = formatTime(data.last_scrape_time);
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

/**
 * Load and display predictions
 */
async function loadPredictions() {
    try {
        const response = await fetch('/api/predictions');
        const data = await response.json();

        // Update prediction count
        const count = data.total_predictions || 0;
        predictionCountEl.textContent = count;

        // Display JSON
        if (jsonData) {
            jsonData.value = JSON.stringify(data, null, 2);
        }

        // Display predictions
        if (!data.predictions || data.predictions.length === 0) {
            noPredictions.style.display = 'block';
            predictionsList.innerHTML = '';
            return;
        }

        noPredictions.style.display = 'none';
        displayPredictions(data.predictions);

    } catch (error) {
        console.error('Error loading predictions:', error);
        noPredictions.textContent = '❌ Error loading predictions';
        noPredictions.style.display = 'block';
    }
}

/**
 * Display predictions in grid
 */
function displayPredictions(predictions) {
    predictionsList.innerHTML = '';

    predictions.forEach((pred, index) => {
        const card = createPredictionCard(pred);
        predictionsList.appendChild(card);
    });
}

/**
 * Create a prediction card element
 */
function createPredictionCard(prediction) {
    const card = document.createElement('div');
    card.className = 'prediction-card';

    const homeTeam = prediction.home_team || 'Unknown';
    const awayTeam = prediction.away_team || 'Unknown';
    const pred = prediction.prediction || 'TBD';
    const score = prediction.score || '-';
    const betType = prediction.bet_type || 'View';
    const odds = prediction.odds || ['-', '-', '-'];
    const time = prediction.timestamp ? formatTime(prediction.timestamp) : 'Unknown time';
    
    // Create match ID from team names
    const matchId = homeTeam.toLowerCase().replace(/\s+/g, '-') + '_vs_' + awayTeam.toLowerCase().replace(/\s+/g, '-');

    // Labels for odds: 1 = Home, X = Draw, 2 = Away
    const oddLabels = ['1', 'X', '2'];

    // Format odds display with labels
    let oddsHtml = '';
    if (odds && odds.length > 0) {
        if (Array.isArray(odds)) {
            oddsHtml = odds.map((odd, i) => {
                const label = oddLabels[i] || '-';
                return `<div class="odd"><div class="odd-label">${label}</div><div class="odd-value">${escapeHtml(String(odd))}</div></div>`;
            }).join('');
        } else {
            oddsHtml = `<div class="odd"><div class="odd-label">-</div><div class="odd-value">${escapeHtml(String(odds))}</div></div>`;
        }
    } else {
        oddsHtml = '<div class="odd"><div class="odd-label">1</div><div class="odd-value">-</div></div><div class="odd"><div class="odd-label">X</div><div class="odd-value">-</div></div><div class="odd"><div class="odd-label">2</div><div class="odd-value">-</div></div>';
    }

    card.innerHTML = `
        <div class="prediction-teams">
            <div class="team">${escapeHtml(homeTeam)}</div>
            <div class="vs-divider">vs</div>
            <div class="team">${escapeHtml(awayTeam)}</div>
        </div>
        <div class="prediction-info">
            <div class="prediction-score">${escapeHtml(pred)}</div>
            <div class="prediction-score-detail">${escapeHtml(score)}</div>
            <div class="bet-type">${escapeHtml(betType)}</div>
            <div class="odds-display">
                ${oddsHtml}
            </div>
        </div>
        <div class="prediction-meta">
            <small>📅 ${time}</small>
        </div>
        <div class="card-footer">
            <button class="view-details-btn">View Details</button>
        </div>
    `;

    // Add click handler to view details
    const detailsBtn = card.querySelector('.view-details-btn');
    detailsBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        showMatchDetails(homeTeam + ' vs ' + awayTeam, matchId);
    });

    return card;

}

/**
 * Update UI based on status
 */
function updateUI(status) {
    statusBadge.className = 'status-badge';
    
    switch(status) {
        case 'scraping':
            statusBadge.textContent = 'Scraping...';
            statusBadge.classList.add('scraping');
            scrapeBtn.disabled = true;
            break;
        case 'ready':
            statusBadge.textContent = 'Ready';
            statusBadge.classList.add('ready');
            scrapeBtn.disabled = false;
            break;
        case 'error':
            statusBadge.textContent = 'Error';
            statusBadge.classList.add('error');
            scrapeBtn.disabled = false;
            break;
    }
}

/**
 * Show/hide loading spinner
 */
function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
}

/**
 * Toggle JSON section visibility
 */
function toggleJson() {
    const content = document.querySelector('.json-content');
    content.classList.toggle('hidden');
    jsonHeader.classList.toggle('collapsed');
}

/**
 * Download JSON file
 */
function downloadJson() {
    const data = jsonData.value;
    const element = document.createElement('a');
    element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(data));
    element.setAttribute('download', `predictions-${formatDateForFile(new Date())}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/**
 * Format timestamp for display
 */
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const today = new Date();
    
    if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString();
    }
    
    return date.toLocaleString();
}

/**
 * Format date for filename
 */
function formatDateForFile(date) {
    return date.toISOString().split('T')[0] + '_' + 
           date.getHours().toString().padStart(2, '0') + 
           date.getMinutes().toString().padStart(2, '0');
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show match details modal
 */
async function showMatchDetails(matchTitle, matchId) {
    try {
        // Create modal if it doesn't exist
        let modal = document.getElementById('detailsModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'detailsModal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Match Details</h2>
                        <span class="close-btn">&times;</span>
                    </div>
                    <div class="modal-body" id="modalBody">
                        <p style="text-align: center;">Loading details...</p>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Close button handler
            modal.querySelector('.close-btn').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            
            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        modal.style.display = 'block';
        const modalBody = document.getElementById('modalBody');
        
        // Update header with match title
        modal.querySelector('h2').textContent = matchTitle;
        
        // Fetch match details from API
        const response = await fetch(`/api/match-details/${matchId}`);
        const details = await response.json();
        
        // Display details
        let html = `<div class="match-details">`;
        
        if (details.error) {
            html += `<p class="error">Could not load details: ${escapeHtml(details.error)}</p>`;
        } else {
            // Match Preview
            if (details.preview) {
                html += `<div class="detail-section">
                    <h3>📋 Match Preview</h3>
                    <p>${escapeHtml(details.preview)}</p>
                </div>`;
            }
            
            // Team Form section
            if (details.team_form) {
                html += `<div class="detail-section">
                    <h3>📊 Team Form</h3>
                    <div class="form-comparison">`;
                
                // Home team form
                if (details.team_form.home) {
                    const home = details.team_form.home;
                    html += `<div class="team-form-block">
                        <h4>${escapeHtml(home.team)}</h4>
                        <div class="form-stat">Form: <span class="form-value">${escapeHtml(home.form)}</span></div>
                        <div class="form-stat">Home: <span class="form-value">${escapeHtml(home.home_record)}</span></div>
                        <div class="form-stat">Away: <span class="form-value">${escapeHtml(home.away_record)}</span></div>
                        <div class="last-games">
                            <strong>Last 5 Games:</strong>
                            <ul>`;
                    home.last_5_games.forEach(game => {
                        const resultClass = game.result === 'W' ? 'win' : game.result === 'D' ? 'draw' : 'loss';
                        html += `<li><span class="result-badge ${resultClass}">${game.result}</span> ${escapeHtml(game.score)} vs ${escapeHtml(game.opponent)}</li>`;
                    });
                    html += `</ul></div></div>`;
                }
                
                // Away team form
                if (details.team_form.away) {
                    const away = details.team_form.away;
                    html += `<div class="team-form-block">
                        <h4>${escapeHtml(away.team)}</h4>
                        <div class="form-stat">Form: <span class="form-value">${escapeHtml(away.form)}</span></div>
                        <div class="form-stat">Home: <span class="form-value">${escapeHtml(away.home_record)}</span></div>
                        <div class="form-stat">Away: <span class="form-value">${escapeHtml(away.away_record)}</span></div>
                        <div class="last-games">
                            <strong>Last 5 Games:</strong>
                            <ul>`;
                    away.last_5_games.forEach(game => {
                        const resultClass = game.result === 'W' ? 'win' : game.result === 'D' ? 'draw' : 'loss';
                        html += `<li><span class="result-badge ${resultClass}">${game.result}</span> ${escapeHtml(game.score)} vs ${escapeHtml(game.opponent)}</li>`;
                    });
                    html += `</ul></div></div>`;
                }
                
                html += `</div></div>`;
            }
            
            // Head-to-Head section
            if (details.head_to_head) {
                const h2h = details.head_to_head;
                html += `<div class="detail-section">
                    <h3>🏆 Head-to-Head Record</h3>
                    <div class="h2h-stats">
                        <div class="h2h-stat"><span class="stat-label">Wins:</span> ${escapeHtml(String(h2h.home_wins))} - ${escapeHtml(String(h2h.away_wins))}</div>
                        <div class="h2h-stat"><span class="stat-label">Draws:</span> ${escapeHtml(String(h2h.draws))}</div>
                        <div class="h2h-stat"><span class="stat-label">Avg Goals:</span> ${escapeHtml(String(h2h.avg_goals))}</div>
                    </div>
                    <table class="h2h-table">
                        <tr><th>Date</th><th>Location</th><th>Result</th><th>Winner</th></tr>`;
                h2h.last_5_meetings.forEach(meeting => {
                    html += `<tr>
                        <td>${escapeHtml(meeting.date)}</td>
                        <td>${escapeHtml(meeting.location)}</td>
                        <td>${escapeHtml(meeting.result)}</td>
                        <td>${escapeHtml(meeting.winner)}</td>
                    </tr>`;
                });
                html += `</table></div>`;
            }
            
            // Match Statistics section
            if (details.match_statistics) {
                const stats = details.match_statistics;
                html += `<div class="detail-section">
                    <h3>📈 Match Statistics</h3>
                    <table class="stats-table">
                        <tr>
                            <th>${escapeHtml(stats.home.team)}</th>
                            <th>Statistic</th>
                            <th>${escapeHtml(stats.away.team)}</th>
                        </tr>`;
                
                const comparisons = [
                    { label: 'Avg Goals For', home: 'avg_goals_for', away: 'avg_goals_for' },
                    { label: 'Avg Goals Against', home: 'avg_goals_against', away: 'avg_goals_against' },
                    { label: 'Possession %', home: 'possession_pct', away: 'possession_pct' },
                    { label: 'Shots/Game', home: 'shots_per_game', away: 'shots_per_game' },
                    { label: 'Shots on Target', home: 'shots_on_target', away: 'shots_on_target' },
                    { label: 'Corners/Game', home: 'corners_per_game', away: 'corners_per_game' },
                    { label: 'Clean Sheets', home: 'clean_sheets', away: 'clean_sheets' }
                ];
                
                comparisons.forEach(comp => {
                    const homeVal = stats.home[comp.home];
                    const awayVal = stats.away[comp.away];
                    html += `<tr>
                        <td><strong>${escapeHtml(String(homeVal))}</strong></td>
                        <td>${escapeHtml(comp.label)}</td>
                        <td><strong>${escapeHtml(String(awayVal))}</strong></td>
                    </tr>`;
                });
                
                html += `</table></div>`;
            }
            
            // Odds Comparison section
            if (details.odds_comparison) {
                const odds = details.odds_comparison;
                html += `<div class="detail-section">
                    <h3>💰 Odds Comparison</h3>
                    <div class="odds-grid">
                        <div class="odds-column">
                            <h4>Home Win</h4>`;
                odds.home_win.forEach(o => {
                    html += `<div class="odds-row"><span>${escapeHtml(o.bookmaker)}</span> <strong>${escapeHtml(o.odds)}</strong></div>`;
                });
                html += `</div>
                        <div class="odds-column">
                            <h4>Draw</h4>`;
                odds.draw.forEach(o => {
                    html += `<div class="odds-row"><span>${escapeHtml(o.bookmaker)}</span> <strong>${escapeHtml(o.odds)}</strong></div>`;
                });
                html += `</div>
                        <div class="odds-column">
                            <h4>Away Win</h4>`;
                odds.away_win.forEach(o => {
                    html += `<div class="odds-row"><span>${escapeHtml(o.bookmaker)}</span> <strong>${escapeHtml(o.odds)}</strong></div>`;
                });
                html += `</div></div></div>`;
            }
        }
        
        html += `</div>`;
        modalBody.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading match details:', error);
        document.getElementById('modalBody').innerHTML = `<p class="error">Error loading details: ${error.message}</p>`;
    }
}

