from celery import shared_task

from bots.status_checker import fetch_claim_status, save_log


@shared_task
def check_claim_status(claim_number):
    try:
        details = fetch_claim_status(claim_number, True)
    except Exception as error:
        save_log(claim_number, "error", str(error), {})
        raise

    if details is None:
        save_log(claim_number, "not_found", "Claim not found on portal", {})
        return "not_found"

    save_log(claim_number, "success", "Claim status fetched from portal", details)
    return details