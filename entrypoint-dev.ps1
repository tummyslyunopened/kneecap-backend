# Run migrations before starting runtime processes
uv run manage.py makemigrations
uv run manage.py migrate

# Start each process and redirect output and error to separate log files
Start-Process -FilePath "uv" -ArgumentList "run manage.py runserver 0.0.0.0:80" -RedirectStandardOutput "./logs/runserver-output.log" -RedirectStandardError "./logs/runserver-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py rss-episode-downloader" -RedirectStandardOutput "./logs/rss-episode-downloader-output.log" -RedirectStandardError "./logs/rss-episode-downloader-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py rss-subscriptions-refresher" -RedirectStandardOutput "./logs/rss-subscriptions-refresher-output.log" -RedirectStandardError "./logs/rss-subscriptions-refresher-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py rss-q-subscriptions" -RedirectStandardOutput "./logs/rss-q-subscriptions-output.log" -RedirectStandardError "./logs/rss-q-subscriptions-error.log" -NoNewWindow

# Use Get-Content to follow the logs
Get-Content ./logs/runserver-output.log, ./logs/runserver-error.log, ./logs/rss-episode-downloader-output.log, ./logs/rss-episode-downloader-error.log, ./logs/rss-subscriptions-refresher-output.log, ./logs/rss-subscriptions-refresher-error.log, ./logs/rss-q-subscriptions-output.log, ./logs/rss-q-subscriptions-error.log -Wait
