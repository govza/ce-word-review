# Local-only credentials; change them before exposing the server beyond localhost.
$env:PYTHONIOENCODING = 'utf-8'
& "$PSScriptRoot\.venv\Scripts\label-studio.exe" start ce-word-review --init `
    --label-config "$PSScriptRoot\label_config.xml" `
    --data-dir "$PSScriptRoot\data" `
    --username reviewer@example.com --password chechen-review `
    --user-token local-review-token --enable-legacy-api-token `
    --port 8080
