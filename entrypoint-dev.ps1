# Create logs directory if it doesn't exist
if (!(Test-Path -Path './logs')) {
    New-Item -ItemType Directory -Path './logs' | Out-Null
}

# Run migrations before starting runtime processes
uv run manage.py makemigrations
uv run manage.py migrate

# Start each process and redirect output and error to separate log files
Start-Process -FilePath "uv" -ArgumentList "run manage.py runserver 0.0.0.0:80" -RedirectStandardOutput "./logs/runserver-output.log" -RedirectStandardError "./logs/runserver-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py sync_rss_data" -RedirectStandardOutput "./logs/sync-rss-data-output.log" -RedirectStandardError "./logs/sync-rss-data-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py download_media" -RedirectStandardOutput "./logs/download-media-output.log" -RedirectStandardError "./logs/download-media-error-log" -NoNewWindow

# Use Get-Content to follow the logs
Get-Content ./logs/runserver-output.log, ./logs/runserver-error.log, ./logs/sync-rss-data-output.log, ./logs/sync-rss-data-error.log, ./logs/download-media-output.log, ./logs/download-media-error-log -Wait
