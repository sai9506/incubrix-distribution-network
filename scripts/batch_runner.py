
import json
import logging
import sys

from datetime import datetime, timezone
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.api.routes import service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

INPUT_FILE = PROJECT_ROOT / "batch_input.json"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "batch_manifest.json"


def run_batch():
    if not INPUT_FILE.exists():
        logger.error("Batch input file not found: %s", INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        requests = json.load(file)

    if not isinstance(requests, list):
        logger.error("Batch input must contain a JSON list")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for index, request_data in enumerate(requests, start=1):
        logger.info(
            "Processing batch item %s of %s",
            index,
            len(requests)
        )

        try:
            platform = request_data["platform"]

            content = {
                "title": request_data["title"],
                "body": request_data["body"],
                "tags": request_data.get("tags", []),
                "ai_generated": request_data.get("ai_generated", False),
                "ai_disclosure": request_data.get("ai_disclosure", False),
                "is_self_promotion": request_data.get(
                    "is_self_promotion", False
                ),
                "self_promo_disclosure": request_data.get(
                    "self_promo_disclosure", False
                )
            }

            # Safe by default: preview only
            dry_run = request_data.get("dry_run", True)

            result = service.publish(
                platform=platform,
                content=content,
                recent_posts=0,
                dry_run=dry_run
            )

            item_result = {
                "item_number": index,
                "platform": platform,
                "title": content["title"],
                "status": result.get("status", "unknown"),
                "result": result
            }

        except Exception:
            logger.exception("Batch item %s failed", index)

            item_result = {
                "item_number": index,
                "platform": request_data.get("platform", "unknown"),
                "title": request_data.get("title", "unknown"),
                "status": "failed",
                "result": {
                    "message": "Batch item processing error"
                }
            }

        results.append(item_result)

    manifest = {
        "batch_status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(results),
        "successful": sum(
            1 for item in results
            if item["status"] in ["success", "preview", "manual_required"]
        ),
        "blocked": sum(
            1 for item in results if item["status"] == "blocked"
        ),
        "failed": sum(
            1 for item in results if item["status"] == "failed"
        ),
        "results": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    logger.info("Batch processing completed")
    logger.info("Manifest saved to: %s", OUTPUT_FILE)
    logger.info(
        "Total: %s | Successful: %s | Blocked: %s | Failed: %s",
        manifest["total_items"],
        manifest["successful"],
        manifest["blocked"],
        manifest["failed"]
    )

    return manifest


if __name__ == "__main__":
    run_batch()
