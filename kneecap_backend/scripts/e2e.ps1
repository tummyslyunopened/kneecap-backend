scripts/rip-migrations.ps1
Start-Sleep -Seconds 5
python manage.py makemigrations
Start-Sleep -Seconds 5
python manage.py migrate
Start-Sleep -Seconds 5
scripts/import-opml.ps1 "scripts/.data/example.opml"
Start-Sleep -Seconds 5
python manage.py update_mirrors
Start-Sleep -Seconds 5
python manage.py update_episodes
Start-Sleep -Seconds 5
python manage.py download_episodes --hours 240