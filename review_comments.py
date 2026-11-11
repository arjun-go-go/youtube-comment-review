"""Turn a saved YouTube Comments Scraper JSON export into two review CSVs."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


COMMENT_FIELDS = [
    "video_id", "video_title", "comment_id", "parent_comment_id", "is_reply",
    "comment_text", "parent_comment_text", "parent_in_export", "comment_url",
    "like_count", "collected_at", "review_topic", "next_action", "owner", "review_status",
]
STATUS_FIELDS = [
    "input_value", "video_id", "status", "error_code", "message", "suggestion", "collected_at",
]


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def export_review(source, output):
    raw = source.read_bytes()
    records = json.loads(raw.decode("utf-8-sig"))
    comments = {}
    statuses = []
    duplicates = 0
    for record in records:
        if record.get("recordType") == "comment":
            key = (record["videoId"], record["commentId"])
            if key in comments:
                duplicates += 1
                continue
            comments[key] = record
        elif record.get("recordType") == "videoStatus":
            statuses.append(record)

    review_rows = []
    for record in comments.values():
        parent_id = record.get("parentCommentId")
        parent = comments.get((record["videoId"], parent_id))
        review_rows.append({
            "video_id": record["videoId"],
            "video_title": record.get("videoTitle", ""),
            "comment_id": record["commentId"],
            "parent_comment_id": parent_id or "",
            "is_reply": str(record.get("isReply", False)).lower(),
            "comment_text": record.get("text", ""),
            "parent_comment_text": parent.get("text", "") if parent else "",
            "parent_in_export": str(parent is not None).lower() if parent_id else "",
            "comment_url": record.get("commentUrl", ""),
            "like_count": record.get("likeCount"),
            "collected_at": record.get("scrapedAt", ""),
            "review_topic": "", "next_action": "", "owner": "",
            "review_status": "not_reviewed",
        })
    status_rows = [{
        "input_value": r.get("inputValue", ""), "video_id": r.get("videoId", ""),
        "status": r.get("status", ""), "error_code": r.get("errorCode", ""),
        "message": r.get("errorMessage", ""), "suggestion": r.get("suggestion", ""),
        "collected_at": r.get("scrapedAt", ""),
    } for r in statuses]
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "comments-review.csv", COMMENT_FIELDS, review_rows)
    write_csv(output / "collection-status.csv", STATUS_FIELDS, status_rows)
    summary = {
        "source_file": source.name,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "input_records": len(records), "comments": len(review_rows),
        "parents": sum(not r.get("isReply", False) for r in comments.values()),
        "replies": sum(bool(r.get("isReply", False)) for r in comments.values()),
        "duplicate_comments_removed": duplicates,
        "status_records": len(status_rows),
        "status_counts": dict(Counter(r.get("status", "") for r in statuses)),
        "other_record_types": len(records) - len(comments) - duplicates - len(statuses),
        "replies_with_parent_in_export": sum(r["parent_in_export"] == "true" for r in review_rows),
        "network_requests": 0,
    }
    (output / "export-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON array exported from the Actor")
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    export_review(args.input, args.out)
