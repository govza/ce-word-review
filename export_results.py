"""Export reviewed words from the running Label Studio project as a CSV shaped like the input sheet.

Usage: python export_results.py [exports/reviewed.csv]
"""
import csv
import html
import io
import re
import sys
import urllib.request
from pathlib import Path

EXPORT_URL = "http://localhost:8080/api/projects/1/export?exportType=CSV"
TOKEN = "local-review-token"
SHEET_HEADER = ["№", "Контекст (слово для оценки выделено жирным)", "Слово",
                "1. Чья это речь?", "2. Что это за слово?", "Комментарий (по желанию)"]


def plain_context(highlighted: str) -> str:
    return html.unescape(re.sub(r"</?b>", "", highlighted))


assert plain_context("a &lt;<b>тата</b>&gt; татам") == "a <тата> татам"

if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "exports/reviewed.csv")
    request = urllib.request.Request(EXPORT_URL, headers={"Authorization": f"Token {TOKEN}"})
    with urllib.request.urlopen(request) as response:
        rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8"))))
    rows.sort(key=lambda r: int(r["id"]))

    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(SHEET_HEADER)
        for number, r in enumerate(rows, 1):
            writer.writerow([number, plain_context(r["context"]), r["word"],
                             r.get("speech", ""), r.get("kind", ""), r.get("comment", "")])
    print(f"{len(rows)} rows -> {target}")
