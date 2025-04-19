# Create log files if they do not exist
if (-not (Test-Path "runserver.log")) { New-Item "runserver.log" -ItemType File }
if (-not (Test-Path "rss-episode-downloader.log")) { New-Item "rss-episode-downloader.log" -ItemType File }
if (-not (Test-Path "rss-subscriptions-refresher.log")) { New-Item "rss-subscriptions-refresher.log" -ItemType File }

# Start each process and redirect output and error to separate log files
Start-Process -FilePath "uv" -ArgumentList "run manage.py runserver 0.0.0.0:80" -RedirectStandardOutput "runserver-output.log" -RedirectStandardError "runserver-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py rss-episode-downloader" -RedirectStandardOutput "rss-episode-downloader-output.log" -RedirectStandardError "rss-episode-downloader-error.log" -NoNewWindow
Start-Process -FilePath "uv" -ArgumentList "run manage.py rss-subscriptions-refresher" -RedirectStandardOutput "rss-subscriptions-refresher-output.log" -RedirectStandardError "rss-subscriptions-refresher-error.log" -NoNewWindow

# Use Get-Content to follow the logs
Get-Content runserver-output.log, runserver-error.log, rss-episode-downloader-output.log, rss-episode-downloader-error.log, rss-subscriptions-refresher-output.log, rss-subscriptions-refresher-error.log -Wait