# word-review

Label Studio project for native keep/drop review of doubtful words, keyboard only.

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

## Reinstall

```
python -m venv .venv
uv pip install --python .venv/Scripts/python.exe label-studio
```

Plain `pip install label-studio` stalled on Python 3.13; `uv` took under a minute.
