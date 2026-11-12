"""Convert a review sheet export (CSV or TSV) into Label Studio tasks.

Columns are found by header: "Контекст…", "Слово", "1. …", "2. …", "Комментарий…".
Answers already in the sheet become pre-annotations.

Usage: python make_tasks.py sheet.csv tasks.json
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE / "ce-corpus-toolkit"))
from russian_filter import load_ru_frequencies  # noqa: E402

DICTIONARIES = {
    "RU словарь": load_ru_frequencies(str(WORKSPACE / "aosp-dictionaries/wordlists/main_ru.combined")),
    "CE словарь": load_ru_frequencies(str(WORKSPACE / "ce-corpus-toolkit/exports/main_ce.combined")),
}

ANSWER_COLUMNS = {"speech": ("1.", "choices"), "kind": ("2.", "choices"), "comment": ("Комментарий", "textarea")}


def highlight(context: str, word: str) -> str:
    pattern = rf"(?<!\w){re.escape(html.escape(word))}(?!\w)"
    return re.sub(pattern, lambda m: f"<b>{m.group(0)}</b>", html.escape(context), flags=re.IGNORECASE)


def column(row: dict, prefix: str) -> str:
    return next((v or "" for k, v in row.items() if k.strip().startswith(prefix)), "").strip()


def dictionary_info(word: str) -> str:
    key = word.lower().replace("ё", "е")
    return " · ".join(
        f"{label}: f={freqs[key]}" if key in freqs else f"{label}: нет"
        for label, freqs in DICTIONARIES.items()
    )


def to_task(row: dict) -> dict:
    word = column(row, "Слово")
    task = {"data": {"context": highlight(column(row, "Контекст"), word), "word": word,
                     "info": dictionary_info(word)}}
    result = [
        {"from_name": name, "to_name": "ctx", "type": kind,
         "value": {"choices": [answer]} if kind == "choices" else {"text": [answer]}}
        for name, (prefix, kind) in ANSWER_COLUMNS.items()
        if (answer := column(row, prefix))
    ]
    if result:
        task["predictions"] = [{"model_version": "sheet", "result": result}]
    return task


assert highlight("a <тата> татам", "тата") == "a &lt;<b>тата</b>&gt; татам"

if __name__ == "__main__":
    source, target = sys.argv[1], sys.argv[2]
    with open(source, encoding="utf-8-sig", newline="") as f:
        delimiter = "\t" if "\t" in f.readline() else ","
        f.seek(0)
        tasks = [to_task(row) for row in csv.DictReader(f, delimiter=delimiter) if column(row, "Слово")]
    with open(target, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=1)
    prelabeled = sum("predictions" in t for t in tasks)
    print(f"{len(tasks)} tasks ({prelabeled} pre-labeled) -> {target}")
