# word-review

Review doubtful Chechen dictionary words one by one, using only the keyboard. Runs [Label Studio](https://labelstud.io/) locally on Windows.

For each word you see its sentence, whether it is in the Russian and Chechen dictionaries, and answer two questions:

1. Whose speech is it? (Chechen / Russian)
2. What kind of word is it? (ordinary, loanword, Russian, name, abbreviation, typo)

## What you need

- Windows with PowerShell
- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- About 700 MB of free disk
- This folder next to `ce-corpus-toolkit` and `aosp-dictionaries` (see the workspace `README.md`)

## Install (once)

Run in PowerShell, inside this folder:

```powershell
python -m venv .venv
uv pip install --python .venv/Scripts/python.exe label-studio
```

Use `uv` here: plain `pip install label-studio` stalled on Python 3.13.

## Start

```powershell
./start.ps1
```

Wait about a minute, then open http://localhost:8080 and log in:

- Email: `reviewer@example.com`
- Password: `chechen-review`

Keep the PowerShell window open while you work. Close it to stop the server.

If PowerShell refuses to run the script, use `powershell -ExecutionPolicy Bypass -File start.ps1`.

## Load words (once per batch)

The first start creates an empty project, `ce-word-review`. With the server running, open a second PowerShell window in this folder:

```powershell
python make_tasks.py blind_100.csv tasks.json
curl.exe -H "Authorization: Token local-review-token" -H "Content-Type: application/json" --data-binary "@tasks.json" http://localhost:8080/api/projects/1/import
```

Running the second command twice loads the batch twice.

For a new batch, export the sheet as CSV or TSV and use it in place of `blind_100.csv`. The sheet needs these column headers:

| Header starts with | Content |
|---|---|
| `Контекст` | sentence containing the word |
| `Слово` | the word to review |
| `1.` | speech answer, may be empty |
| `2.` | kind answer, may be empty |
| `Комментарий` | comment, may be empty |

Answers already in the sheet show up pre-selected. They still need `Ctrl+Enter` to count as reviewed.

## Review

Open the project and click **Label All Tasks**. It serves only the words not yet answered. Clicking a row in the table instead walks through every word, answered ones included.

| Key | Answer |
|---|---|
| `f` | чеченская |
| `j` | русская |
| `1` | обычное слово |
| `2` | заимствование |
| `3` | русское |
| `4` | имя / название |
| `5` | опечатка |
| `6` | сокращение |
| `Ctrl+Enter` | submit and go to the next word |
| `Ctrl+Space` | skip |

The line under the word shows the dictionary lookup, for example `RU словарь: f=57 · CE словарь: f=114`. `f` is the frequency, `нет` means the word is absent. The CE dictionary is the list under review, so a word being in it does not make it correct.

## Get the results

With the server running:

```powershell
python export_results.py exports/blind_100_reviewed.csv
```

The file has the same columns as the input sheet, with the answers filled in, so it can be pasted back into the sheet. Rows are numbered in import order.

Your answers are stored only in `data/` and `exports/`, and neither is in git. Export regularly as a backup.

## Other reviewers

The server answers only on this machine. To let someone else review, expose port 8080 through a tunnel or host it on a server, and first change the email, password and token in `start.ps1`.

## Files

| File | Purpose |
|---|---|
| `start.ps1` | starts the server and creates the project on first run |
| `label_config.xml` | the review screen: questions, answers, hotkeys |
| `make_tasks.py` | turns a sheet export into Label Studio tasks |
| `export_results.py` | writes the answers to `exports/` in the input sheet's format |
| `blind_100.csv` | first batch of 100 words |
| `exports/` | exported results (not in git) |
| `data/` | Label Studio database with your answers (not in git) |
