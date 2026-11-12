# ce-word-review

Review doubtful Chechen dictionary words one by one, using only the keyboard. Runs [Label Studio](https://labelstud.io/) locally on Windows.

For each word you see its sentence, whether it is in the Russian and Chechen dictionaries, and answer two questions:

1. Whose speech is it? (Chechen / Russian)
2. What kind of word is it? (ordinary, loanword, Russian, name, typo, abbreviation)

## Workflow at a glance

```
sheet (CSV)  ->  imports/batch.csv  ->  make_tasks.py  ->  tasks.json  ->  Label Studio
                                                                              |
sheet (CSV)  <-  exports/batch_reviewed.csv  <-  export_results.py  <---------+
```

| Step | You do | Result lands in |
|---|---|---|
| 1 | Export the sheet as CSV | `imports/` |
| 2 | Convert and load it | the Label Studio project |
| 3 | Answer with hotkeys | `data/` (Label Studio database) |
| 4 | Export the answers | `exports/` |

`imports/`, `exports/` and `data/` are not in git: they hold corpus text and your answers.

## What you need

- Windows with PowerShell
- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- About 700 MB of free disk
- This folder next to checkouts of [`ce-corpus-toolkit`](https://github.com/govza/ce-corpus-toolkit) (branch `feat/ru-span-filter`, with `exports/main_ce.combined` built) and [`aosp-dictionaries`](https://codeberg.org/Helium314/aosp-dictionaries). The dictionary lookup reads from both.

## Install (once)

Run in PowerShell, inside this folder:

```powershell
python -m venv .venv
uv pip install --python .venv/Scripts/python.exe label-studio
```

Use `uv` here: plain `pip install label-studio` stalled on Python 3.13.

## Start the server

```powershell
./start.ps1
```

Wait about a minute, then open http://localhost:8080 and log in:

- Email: `reviewer@example.com`
- Password: `chechen-review`

Keep the PowerShell window open while you work. Close it to stop the server. The first start creates an empty project, `ce-word-review`.

If PowerShell refuses to run the script, use `powershell -ExecutionPolicy Bypass -File start.ps1`.

## Step 1: prepare the input CSV

Export the sheet as CSV (comma-separated) or TSV (tab-separated), UTF-8, and save it in `imports/`.

The first row must be a header. Columns are found by how the header starts, so their order and any extra columns do not matter:

| Header starts with | Required | Content |
|---|---|---|
| `Контекст` | yes | sentence containing the word |
| `Слово` | yes | the word to review, as it appears in the sentence |
| `1.` | no | speech answer, if already known |
| `2.` | no | kind answer, if already known |
| `Комментарий` | no | comment |

Example:

```csv
№,Контекст (слово для оценки выделено жирным),Слово,1. Чья это речь?,2. Что это за слово?,Комментарий (по желанию)
1,"Мичуринан поселок йолчу агӏора баьхкира",поселок,,,
2,"бошхепийн тата а деш",тата,чеченская,обычное слово,шум/звук
```

Rows with an empty `Слово` are ignored. Answers must use the exact values from the hotkey table below, otherwise they are not pre-selected.

## Step 2: load the batch

With the server running, open a second PowerShell window in this folder:

```powershell
python make_tasks.py imports/batch.csv tasks.json
curl.exe -H "Authorization: Token local-review-token" -H "Content-Type: application/json" --data-binary "@tasks.json" http://localhost:8080/api/projects/1/import
```

The first command prints how many words it converted. It bolds the word in its sentence and adds the dictionary lookup. The second command prints `"task_count"` with the number loaded.

- New batches are added to the same project, after the existing words.
- There is no duplicate check: running the second command twice loads the batch twice.
- Answers already in the sheet show up pre-selected. They still need `Ctrl+Enter` to count as reviewed.

## Step 3: review

Open the project and click **Label All Tasks**. It serves only the words not yet answered. Clicking a row in the table instead walks through every word, answered ones included.

| Key | Question | Answer |
|---|---|---|
| `f` | 1 | чеченская |
| `j` | 1 | русская |
| `1` | 2 | обычное слово |
| `2` | 2 | заимствование |
| `3` | 2 | русское |
| `4` | 2 | имя / название |
| `5` | 2 | опечатка |
| `6` | 2 | сокращение |
| `Ctrl+Enter` | | submit and go to the next word |
| `Ctrl+Space` | | skip |

The line under the word shows the dictionary lookup, for example `RU словарь: f=57 · CE словарь: f=114`. `f` is the frequency, `нет` means the word is absent. The CE dictionary is the list under review, so a word being in it does not make it correct.

## Step 4: export the answers

With the server running:

```powershell
python export_results.py exports/batch_reviewed.csv
```

Without an argument it writes `exports/reviewed.csv`. An existing file with the same name is overwritten.

The output has the same six columns as the example in step 1, UTF-8, comma-separated, so it can be pasted back into the sheet:

| Column | Content |
|---|---|
| `№` | running number, in the order the words were loaded |
| `Контекст…` | the sentence, as in the input |
| `Слово` | the word |
| `1. Чья это речь?` | your speech answer |
| `2. Что это за слово?` | your kind answer |
| `Комментарий…` | your comment |

It contains every word in the project, from all batches. Words not yet answered have empty answer columns.

Your answers exist only in `data/` and in the files you export. Export regularly as a backup.

## Other reviewers

The server answers only on this machine. To let someone else review, expose port 8080 through a tunnel or host it on a server, and first change the email, password and token in `start.ps1` (the token also appears in `export_results.py` and in the step 2 command).

## Files

| File | Purpose |
|---|---|
| `start.ps1` | starts the server and creates the project on first run |
| `label_config.xml` | the review screen: questions, answers, hotkeys |
| `make_tasks.py` | turns an input CSV into Label Studio tasks |
| `export_results.py` | writes the answers to `exports/` in the input format |
| `imports/` | input CSVs (not in git) |
| `exports/` | exported answers (not in git) |
| `data/` | Label Studio database (not in git) |

## License

MIT, see `LICENSE`.
