# Firestore Integration & Cloud Function Setup Guide

## Overview
This project now includes automated hourly scraping with Firestore integration. Predictions are scraped from predictz.com every hour using Google Cloud Functions and stored in Firestore for Android app consumption.

## Architecture

```
Cloud Scheduler (hourly trigger)
         ↓
    Cloud Function
         ↓
   PredictzScraper
         ↓
    Firestore Database
         ↓
  Android App (read predictions)
```

Local Flask app also syncs to Firestore on manual scrapes.

---

## Setup Instructions

### Step 1: Prepare Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select Project**: "hugingbearer"
3. **Enable Firestore**:
   - Navigate to Firestore Database
   - Click "Create Database"
   - Location: Europe (or your preference)
   - Start in **production mode**
4. **Create Service Account Key**:
   - Project Settings → Service Accounts tab
   - Click "Generate New Private Key"
   - Save the JSON file as `serviceAccountKey.json` in project root

⚠️ **Important**: Do NOT commit `serviceAccountKey.json` to git. Add to `.gitignore`.

### Step 2: Install Dependencies Locally

```bash
pip install -r requirements.txt
```

### Step 3: Test Firestore Connection

```bash
# Set environment variable (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS = "serviceAccountKey.json"

# Test connection
python -c "from firebase_service import initialize_firestore; db = initialize_firestore(); print('✓ Connected!' if db else '✗ Failed')"
```

### Step 4: Run Flask App Locally

```bash
python app.py
```

**New Endpoints**:
- `POST /api/scrape` - Manually trigger scrape (syncs to Firestore)
- `POST /api/sync-firestore` - Manually sync JSON to Firestore
- `GET /api/firestore/latest?limit=5` - Get latest predictions from Firestore
- All existing endpoints still work

### Step 5: Deploy Cloud Function

**Prerequisites**:
- Google Cloud SDK installed (`gcloud` CLI)
- Project ID: `hugingbearer`

```bash
# Authenticate if needed
gcloud auth login

# Set project
gcloud config set project hugingbearer

# Deploy function
cd cloud_function
gcloud functions deploy scrape-predictions-hourly `
  --runtime python311 `
  --trigger-http `
  --allow-unauthenticated `
  --entry-point scrape_predictions `
  --memory 512MB `
  --timeout 60s `
  --region europe-west1 `
  --quiet

cd ..
```

**Output**: Note the `httpsTrigger.url` from deployment

### Step 6: Create Cloud Scheduler Job

1. **Google Cloud Console** → Cloud Scheduler
2. **Create Job**:
   - Name: `scrape-predictions-hourly`
   - Frequency: `0 * * * *` (every hour at :00)
   - Timezone: UTC or your preference
   - Execution timeout: 300 seconds
3. **HTTP Settings**:
   - Method: POST
   - URL: Paste the Cloud Function trigger URL from Step 5
   - Authentication: No auth required (allowed unauthenticated)
   - Click Create

**Test the scheduler**: Click "Force Run" to trigger immediately. Check Cloud Logs for success.

---

## Data Structure in Firestore

**Collection**: `predictions`

**Document structure** (auto-generated IDs):
```json
{
  "timestamp": "2026-04-02T14:30:00.123456",
  "date": "2026-04-02T14:28:45.789012",
  "total_predictions": 47,
  "predictions": [
    {
      "home_team": "Team A",
      "away_team": "Team B",
      "prediction": "1",
      "bet_type": "Home Win",
      "score": "2-1",
      "odds": ["1.86", "3.50", "3.80"],
      "timestamp": "2026-04-02T14:28:45.789012",
      "source": "predictz.com"
    },
    ...
  ],
  "source": "predictz.com"
}
```

---

## Android App Integration

### Firestore Security Rules

Update security rules in Firestore Console (Rules tab):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow public read access to predictions
    match /predictions/{document=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

### Android Code Example (Kotlin)

```kotlin
val db = FirebaseFirestore.getInstance()

// Get latest predictions
db.collection("predictions")
    .orderBy("timestamp", Query.Direction.DESCENDING)
    .limit(1)
    .get()
    .addOnSuccessListener { querySnapshot ->
        for (doc in querySnapshot) {
            val predictions = doc.get("predictions") as List<Map<String, Any>>
            // Display predictions in your UI
        }
    }
    .addOnFailureListener { exception ->
        Log.e("Firestore", "Error fetching predictions", exception)
    }
```

---

## Monitoring

### Cloud Function Logs
```bash
gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 50
```

### Cloud Scheduler Execution History
Google Cloud Console → Cloud Scheduler → scrape-predictions-hourly → View execution history

### Firestore Stats
Google Cloud Console → Firestore → Insights tab

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin==6.2.0
```

### "Service account credentials not found"
- Verify `serviceAccountKey.json` exists in project root
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Restart Flask app after setting env variable

### Cloud Function deployment fails
```bash
# Check gcloud version
gcloud --version

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

### Cloud Scheduler not triggering
1. Verify job is enabled (toggle in job details)
2. Force run a test execution
3. Check Cloud Logs: `gcloud scheduler jobs describe scrape-predictions-hourly --location europe-west1`

### Firestore write fails
- Verify service account has `firestore.databases.update` permission
- Check Firestore is in native mode (not Datastore)
- Verify region matches: europe-west1

---

## API Reference

### Local Flask Endpoints

| Endpoint | Method | Description | Firebase |
|----------|--------|-------------|----------|
| `/api/predictions` | GET | Get all cached predictions from JSON | No |
| `/api/predictions/<limit>` | GET | Get N predictions from JSON | No |
| `/api/scrape` | POST | Trigger scrape (manual, syncs to Firestore) | Yes |
| `/api/sync-firestore` | POST | Sync JSON to Firestore | Yes |
| `/api/firestore/latest` | GET | Get latest predictions from Firestore | Yes |
| `/api/status` | GET | Get scraping status | No |
| `/api/match-details/<id>` | GET | Get match details | No |

### Cloud Function Endpoint

```
POST https://europe-west1-hugingbearer.cloudfunctions.net/scrape-predictions-hourly
```

Triggered automatically by Cloud Scheduler every hour.

---

## Next Steps

1. ✅ Add Firestore integration
2. ✅ Deploy Cloud Function
3. ✅ Create Cloud Scheduler job
4. ✅ Set Firestore security rules
5. 👉 Configure Android app to read from Firestore
6. 👉 Monitor first 24 hours of automatic scrapes
7. 👉 Set up data retention policy (optional)

---

## References

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/database/admin/start#python)
