#!/usr/bin/env bash
# Deploy script for Google Cloud Function
# Usage: bash deploy.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ID="hugingbearer"
FUNCTION_NAME="scrape-predictions-hourly"
REGION="europe-west1"
RUNTIME="python311"

echo "Deploying Cloud Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo ""

echo "[STEP 0] Bundling scraper + Firebase service into cloud_function/..."
mkdir -p "$ROOT/cloud_function/scrapers"
cp "$ROOT/scrapers/predictz_scraper.py" "$ROOT/cloud_function/scrapers/"
cp "$ROOT/scrapers/__init__.py" "$ROOT/cloud_function/scrapers/"
cp "$ROOT/firebase_service.py" "$ROOT/cloud_function/"

echo "[STEP 1] Deploying Cloud Function..."
cd "$ROOT"
gcloud functions deploy "$FUNCTION_NAME" \
  --region "$REGION" \
  --runtime "$RUNTIME" \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point scrape_predictions \
  --memory 512MB \
  --timeout 300s \
  --project "$PROJECT_ID" \
  --source ./cloud_function

echo ""
echo "[OK] Cloud Function deployed successfully!"
echo ""
FUNCTION_URL="$(gcloud functions describe "$FUNCTION_NAME" --region "$REGION" --project "$PROJECT_ID" --format='value(httpsTrigger.url)')"
echo "Trigger URL: $FUNCTION_URL"
echo ""
echo "Create hourly scheduler:"
echo "gcloud scheduler jobs create http scrape-predictions-hourly --location=$REGION --schedule='0 * * * *' --uri=\"$FUNCTION_URL\" --http-method=POST --attempt-deadline=300s --project=$PROJECT_ID"
