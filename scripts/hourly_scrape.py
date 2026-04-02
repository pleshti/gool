"""
Run Predictz scrape and save JSON; optionally sync to Firebase Realtime Database.
Used by GitHub Actions (no Flask / Selenium).
"""
from __future__ import annotations

import json
import os
import sys

# Project root (parent of scripts/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from datetime import datetime

from scrapers.predictz_scraper import PredictzScraper


def main() -> int:
    os.chdir(ROOT)
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    out_path = os.path.join(ROOT, "data", "predictions.json")

    scraper = PredictzScraper(use_selenium=False)
    scraper.scrape()

    data = {
        "date": datetime.now().isoformat(),
        "total_predictions": len(scraper.predictions),
        "predictions": scraper.predictions,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {data['total_predictions']} predictions to {out_path}")

    key_path = os.path.join(ROOT, "serviceAccountKey.json")
    cred_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    has_key = (cred_env and os.path.isfile(cred_env)) or os.path.isfile(key_path)

    if has_key:
        try:
            from firebase_service import store_predictions

            ref = store_predictions(data)
            if ref:
                print(f"Synced to Firebase Realtime Database ({ref})")
            else:
                print("Firebase sync returned no ref (check logs)", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Firebase sync failed: {e}", file=sys.stderr)
            return 1
    else:
        print("No Firebase key in repo — skipped RTDB sync (artifact still uploaded).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
