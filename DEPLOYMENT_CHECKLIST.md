# Deployment Checklist

## Pre-Deployment (Local Testing)

- [ ] Clone or pull latest code
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download `serviceAccountKey.json` from Firebase Console
- [ ] Place `serviceAccountKey.json` in project root
- [ ] Test Firestore connection locally:
  ```bash
  $env:GOOGLE_APPLICATION_CREDENTIALS = "serviceAccountKey.json"
  python -c "from firebase_service import initialize_firestore; initialize_firestore()"
  ```
- [ ] Run Flask app: `python app.py`
- [ ] Test `/api/scrape` endpoint (should sync to Firestore)
- [ ] Verify predictions appear in Firestore Console
- [ ] Test `/api/firestore/latest` endpoint

## GCP Deployment

- [ ] Install Google Cloud SDK: `gcloud init`
- [ ] Authenticate: `gcloud auth login`
- [ ] Set project: `gcloud config set project hugingbearer`
- [ ] Enable APIs:
  ```bash
  gcloud services enable cloudfunctions.googleapis.com
  gcloud services enable cloudbuild.googleapis.com
  gcloud services enable cloudscheduler.googleapis.com
  gcloud services enable firestore.googleapis.com
  ```
- [ ] Deploy Cloud Function:
  ```bash
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
  ```
- [ ] Note the `httpsTrigger.url` output
- [ ] Create Cloud Scheduler job:
  - [ ] Name: `scrape-predictions-hourly`
  - [ ] Frequency: `0 * * * *`
  - [ ] URL: Paste httpsTrigger.url
  - [ ] Method: POST
  - [ ] Timeout: 300s
- [ ] Test scheduler: Click "Force Run"
- [ ] Check Cloud Logs:
  ```bash
  gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 20
  ```

## Post-Deployment

- [ ] Verify first automatic execution in Cloud Logs
- [ ] Check new document in Firestore Console
- [ ] Wait 2 hours to verify second execution
- [ ] Update Android app Firestore security rules:
  ```
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /predictions/{document=**} {
        allow read: if true;
        allow write: if false;
      }
    }
  }
  ```
- [ ] Test Android app can read predictions from Firestore
- [ ] Monitor predictions in Firestore for 24+ hours
- [ ] Set up Firestore backup (optional):
  - [ ] Enable automatic backups in Firestore settings
  - [ ] Monthly retention: ON

## Ongoing Maintenance

- [ ] Monitor Cloud Function logs for errors (weekly)
- [ ] Check Firestore storage usage (monthly)
- [ ] Review prediction quality and count
- [ ] Monitor Cloud Scheduler execution history
- [ ] Update dependencies quarterly (pip)
- [ ] Archive old predictions after 30+ days (optional)

## Rollback Plan

If issues occur:

1. **Disable Cloud Scheduler**:
   ```bash
   gcloud scheduler jobs pause scrape-predictions-hourly --location europe-west1
   ```

2. **Check logs**:
   ```bash
   gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 50
   gcloud scheduler jobs describe scrape-predictions-hourly --location europe-west1
   ```

3. **Revert changes** (if code was the issue):
   ```bash
   git checkout HEAD -- .
   ```

4. **Re-enable scheduler** (after fixing):
   ```bash
   gcloud scheduler jobs resume scrape-predictions-hourly --location europe-west1
   ```

## Monitoring Commands

```bash
# View Cloud Function logs (last 50 lines)
gcloud functions logs read scrape-predictions-hourly --region europe-west1 --limit 50

# View Cloud Scheduler executions
gcloud scheduler jobs describe scrape-predictions-hourly --location europe-west1

# Check deployment status
gcloud functions describe scrape-predictions-hourly --region europe-west1

# View Firestore document count (via Console UI)
# Firestore -> Collections -> predictions -> (check documents)
```

## Support

For issues, check:
1. Cloud Function logs: `gcloud functions logs read scrape-predictions-hourly ...`
2. Cloud Scheduler logs: `gcloud scheduler jobs list --location europe-west1`
3. Firestore Console for data
4. Firebase Service Account permissions
