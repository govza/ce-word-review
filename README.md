# word-review

Label Studio project for native keep/drop review of doubtful words, keyboard only.

## Requirements

- Windows with PowerShell (`start.ps1`), Python 3.10+, [`uv`](https://docs.astral.sh/uv/), about 700 MB disk.
- Sibling folders `../ce-corpus-toolkit` (on a branch that has `russian_filter.py`, with `exports/main_ce.combined` built) and `../aosp-dictionaries`. `make_tasks.py` reads both.
- Reviewers need only a browser, but the server listens on localhost, so they must sit at this machine or reach it through a tunnel.

## First-time setup

```
python -m venv .venv
uv pip install --python .venv/Scripts/python.exe label-studio
./start.ps1
```

Plain `pip install label-studio` stalled on Python 3.13; `uv` took under a minute. If PowerShell refuses to run the script: `powershell -ExecutionPolicy Bypass -File start.ps1`.

The first start creates an empty project `ce-word-review` (id 1). Load words into it with the commands under "Add words", e.g. from `blind_100.csv`.

## Run

```
./start.ps1
```

Opens http://localhost:8080 (login `reviewer@example.com` / `chechen-review`, local only). Data lives in `data/`.

Hotkeys: `1` чеченская, `2` русская; `q` обычное слово, `w` заимствование, `e` русское, `r` имя / название, `t` сокращение, `y` опечатка; `Ctrl+Enter` submit and next.

## Add words

Export the sheet as CSV or TSV (headers `Контекст…`, `Слово`, `1. …`, `2. …`, `Комментарий…`), then:

```
python make_tasks.py sheet.csv tasks.json
curl -H "Authorization: Token local-review-token" -H "Content-Type: application/json" --data-binary @tasks.json http://localhost:8080/api/projects/1/import
```

Each task shows whether the word is in `main_ru.combined` and `main_ce.combined` (with its frequency), looked up when `make_tasks.py` runs.

Answers already in the sheet arrive as pre-annotations, so they show pre-selected and still need `Ctrl+Enter`.

## Get results

Project → Export → CSV. Columns: `context`, `word`, `speech`, `kind`, `comment`.
