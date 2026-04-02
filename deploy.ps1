# Deploy script for Google Cloud Function (PowerShell)
# Usage: .\deploy.ps1
# Bundles scrapers + firebase_service into cloud_function/ then deploys.

$PROJECT_ID = "hugingbearer"
$FUNCTION_NAME = "scrape-predictions-hourly"
$REGION = "europe-west1"
$RUNTIME = "python311"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Deploying Cloud Function: $FUNCTION_NAME" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host ""

if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] gcloud CLI not found. Install Google Cloud SDK first." -ForegroundColor Red
    exit 1
}

# Only cloud_function/ is uploaded; copy shared modules into it for deploy.
Write-Host "[STEP 0] Bundling scraper + Firebase service into cloud_function/..." -ForegroundColor Yellow
$cf = Join-Path $Root "cloud_function"
$scrapersDest = Join-Path $cf "scrapers"
New-Item -ItemType Directory -Force -Path $scrapersDest | Out-Null
Copy-Item (Join-Path $Root "scrapers\predictz_scraper.py") (Join-Path $scrapersDest "predictz_scraper.py") -Force
Copy-Item (Join-Path $Root "scrapers\__init__.py") (Join-Path $scrapersDest "__init__.py") -Force
Copy-Item (Join-Path $Root "firebase_service.py") (Join-Path $cf "firebase_service.py") -Force

Write-Host "[STEP 1] Deploying Cloud Function..." -ForegroundColor Yellow
Push-Location $Root
try {
    gcloud functions deploy $FUNCTION_NAME `
      --region $REGION `
      --runtime $RUNTIME `
      --trigger-http `
      --allow-unauthenticated `
      --entry-point scrape_predictions `
      --memory 512MB `
      --timeout 300s `
      --project $PROJECT_ID `
      --source ./cloud_function `
      --quiet
}
finally {
    Pop-Location
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Cloud Function deployed successfully!" -ForegroundColor Green
    Write-Host ""

    Write-Host "[STEP 2] Getting Cloud Function URL..." -ForegroundColor Yellow
    $functionUrl = gcloud functions describe $FUNCTION_NAME `
      --region $REGION `
      --project $PROJECT_ID `
      --format="value(httpsTrigger.url)"

    Write-Host "Trigger URL: $functionUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Cloud Scheduler (hourly HTTP POST)" -ForegroundColor Cyan
    Write-Host "Console: https://console.cloud.google.com/cloudscheduler?project=$PROJECT_ID" -ForegroundColor White
    Write-Host "Or run (replace URL if needed):" -ForegroundColor White
    Write-Host "gcloud scheduler jobs create http scrape-predictions-hourly --location=$REGION --schedule=`"0 * * * *`" --uri=`"$functionUrl`" --http-method=POST --attempt-deadline=300s --project=$PROJECT_ID" -ForegroundColor Gray
    Write-Host ""
    Write-Host "IAM: Grant the function's service account Firebase/RTDB access if writes fail (e.g. Firebase Admin or Editor on the GCP project)." -ForegroundColor DarkYellow
}
else {
    Write-Host "[ERROR] Deployment failed!" -ForegroundColor Red
    exit 1
}
