# Quick Start Guide - Firestore Integration

## 🚀 Setup (15 minutes total)

### Completed ✓
- [x] Python code written and integrated
- [x] Firebase service account authenticated
- [x] Local Firestore connection working
- [x] Cloud Function code ready
- [x] Deployment scripts created

### What's Left
- [ ] Create Firestore database (4 min)
- [ ] Run local test (2 min)
- [ ] Deploy Cloud Function (5 min)
- [ ] Create Cloud Scheduler job (2 min)

---

## Step-by-Step

### STEP 1: Create Firestore Database (4 minutes)

**Go to**: https://console.firebase.google.com/project/hugingbearer

1. Click **Firestore Database** in left sidebar
2. Click **Create Database** button
3. Select **europe-west1** region
4. Select **Production mode** (secure by default)
5. Click **Create**

⏳ Wait 1-2 minutes for database creation

✓ **Done when**: You see empty "predictions" collection ready

---

### STEP 2: Test Local Setup (2 minutes)

Open PowerShell in project folder:

```powershell
cd c:\Users\user\Desktop\gool

python test_firestore.py
```

**Expected output**:
```
[TEST 1] Testing Firestore connection...
[OK] Connected to Firestore

[TEST 2] Testing data storage...
[OK] Test data stored: ABC123...

[TEST 3] Testing data retrieval...
[OK] Retrieved document: ABC123...

[TEST 4] Testing scraper...
[OK] Scraper initialized

==================================================
[SUCCESS] All tests passed!
```

If you see [SUCCESS], you're ready for deployment!

---

### STEP 3: Deploy Cloud Function (5 minutes)

```powershell
# Make sure you're in the project directory
cd c:\Users\user\Desktop\gool

# Run deployment script
.\deploy.ps1
```

**Expected output**:
```
[STEP 1] Deploying Cloud Function...
[OK] Cloud Function deployed successfully!

[STEP 2] Getting Cloud Function URL...
Trigger URL: https://europe-west1-hugingbearer.cloudfunctions.net/scrape-predictions-hourly
```

📋 **Copy the URL** - you'll need it for the next step

---

### STEP 4: Create Cloud Scheduler Job (5 minutes)

**Go to**: https://console.cloud.google.com/cloudscheduler

1. Click **Create Job**
2. Fill in:
   - **Name**: `scrape-predictions-hourly`
   - **Frequency**: `0 * * * *` (every hour at :00)
   - **Timezone**: UTC (or your preferred timezone)
3. Click **Create**
4. A dialog appears - click **Edit** to configure HTTP
5. Set:
   - **HTTP method**: POST
   - **URL**: Paste the URL from STEP 3
   - **Timeout**: 300 seconds
   - Leave headers blank
6. Click **Save**

✓ **Done when**: Job appears in the list with status "ENABLED"

---

## Testing Scheduled Scraping

### Manual Test (Immediate)
In Cloud Scheduler, click **Force Run** on your job

**Check results**:
1. Open [Google Cloud Logs](https://console.cloud.google.com/logs/)
   ```
   resource.type="cloud_function"
   resource.labels.function_name="scrape-predictions-hourly"
   ```
2. Should show: `[OK] Scrape completed and stored in Firestore`
3. Open [Firestore Console](https://console.firebase.google.com/project/hugingbearer/firestore)
   - Click Collections → predictions
   - Should see new document with latest scrape

### Automatic Test (Real)
- Scheduler will run at the top of every hour
- Check logs hourly to verify it's working
- 24-hour test recommended to confirm

---

## API Endpoints (Local Flask App)

### Start Flask App
```powershell
python app.py
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/api/predictions` | GET | Get predictions from local JSON |
| `/api/predictions/<n>` | GET | Get first N predictions |
| `/api/scrape` | POST | Trigger scrape (syncs to Firestore) |
| `/api/sync-firestore` | POST | Manually sync JSON to Firestore |
| `/api/firestore/latest` | GET | Get latest from Firestore |
| `/api/status` | GET | Get scraping status |

### Example Usage

```bash
# Trigger scrape and sync to Firestore
curl -X POST http://127.0.0.1:5000/api/scrape

# Get latest predictions from Firestore
curl http://127.0.0.1:5000/api/firestore/latest?limit=5

# Check status
curl http://127.0.0.1:5000/api/status
```

---

## Android App Integration

### Firestore Security Rules

Update in [Firestore Console](https://console.firebase.google.com/project/hugingbearer/firestore):

1. Click **Rules** tab
2. Replace with:

```firestore security rules
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

3. Click **Publish**

### Android Code (Kotlin)

```kotlin
val db = FirebaseFirestore.getInstance()

db.collection("predictions")
    .orderBy("timestamp", Query.Direction.DESCENDING)
    .limit(1)
    .get()
    .addOnSuccessListener { snapshot ->
        val doc = snapshot.documents.firstOrNull()
        val predictions = doc?.get("predictions") as? List<Map<String, Any>>
        // Display predictions in your UI
    }
```

---

## Monitoring

### View Cloud Function Logs
```powershell
gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 50
```

### Check Scheduler Executions
Go to Cloud Scheduler → scrape-predictions-hourly → View execution history

### Check Firestore Documents
1. Open Firestore Console
2. Collections → predictions
3. Should see new documents every hour

---

## Troubleshooting

### "Firestore database not found"
- ✓ Did you create the Firestore database in Step 1?
- Go back to Firebase Console and create it

### "Cloud Function deployment fails"
- Verify gcloud CLI is installed: `gcloud --version`
- Login: `gcloud auth login`
- Set project: `gcloud config set project hugingbearer`

### "Scheduler not executing"
- Verify job is ENABLED (toggle if needed)
- Click "Force Run" to test immediately
- Check logs for errors

### "No data in Firestore"
- Run `test_firestore.py` to verify connection
- Check Cloud Function logs for errors
- Verify service account has `firestore.databases.update` permission

---

## Next Steps

1. ✓ Create Firestore database (Step 1)
2. ✓ Test local setup (Step 2)
3. ✓ Deploy Cloud Function (Step 3)
4. ✓ Create Cloud Scheduler (Step 4)
5. → Monitor the first few automatic executions (24 hours)
6. → Configure Android app Firestore rules and query code
7. → Set up Firestore backup (optional, in Firestore settings)

---

## Support

### Files & Locations
- **Service account key**: `serviceAccountKey.json` (git-ignored)
- **Config**: `.env` or environment variables
- **Logs**: Google Cloud Console → Cloud Logs
- **Data**: Firestore Console → Collections → predictions

### Key Commands
```bash
# Test local setup
python test_firestore.py

# Start Flask app
python app.py

# Deploy Cloud Function
.\deploy.ps1

# View Cloud Function logs
gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 50

# Check Firestore connection
python -c "from firebase_service import initialize_firestore; initialize_firestore()"
```

---

**Status**: Ready for Firestore database creation and deployment! 🚀
