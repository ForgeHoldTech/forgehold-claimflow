import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PORTAL_URL = os.environ.get("PORTAL_URL", "http://127.0.0.1:8000/portal/")


def fetch_claim_status(claim_number, headless):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headless,
            slow_mo=0 if headless else 700,
        )
        page = browser.new_page()
        page.goto(PORTAL_URL)
        page.fill("#claim-number-input", claim_number)
        page.click("#search-button")
        page.wait_for_selector("#claim-result, #not-found-message")
        if page.locator("#not-found-message").count() > 0:
            browser.close()
            return None
        details = {
            "patient": page.inner_text("#result-patient"),
            "insurer": page.inner_text("#result-insurer"),
            "amount": page.inner_text("#result-amount"),
            "status": page.inner_text("#result-status"),
        }
        browser.close()
        return details


def save_log(claim_number, result, message, details):
    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27018"))
    database = client[os.environ.get("MONGO_DB", "claimflow_logs")]
    database.bot_logs.insert_one(
        {
            "bot_name": "portal_status_checker",
            "claim_number": claim_number,
            "result": result,
            "message": message,
            "details": details,
            "created_at": datetime.now(timezone.utc),
        }
    )
    client.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python bots/status_checker.py <claim_number> [--show]")
        sys.exit(1)

    claim_number = sys.argv[1]
    headless = "--show" not in sys.argv

    try:
        details = fetch_claim_status(claim_number, headless)
    except Exception as error:
        save_log(claim_number, "error", str(error), {})
        print(f"Bot failed: {error}")
        sys.exit(1)

    if details is None:
        save_log(claim_number, "not_found", "Claim not found on portal", {})
        print(f"Claim {claim_number} was not found on the portal.")
        return

    save_log(claim_number, "success", "Claim status fetched from portal", details)
    print(f"Claim {claim_number} fetched successfully:")
    for key, value in details.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()