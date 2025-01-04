# scripts/rip-migrations.ps2
# Start-Sleep -Seconds 5
# python manage.py makemigrations
rm db.sqlite3
Start-Sleep -Seconds 5
python manage.py migrate
Start-Sleep -Seconds 5
# Copy the command to the clipboard
# "python manage.py runserver" | Set-Clipboard

# # Prompt the user to run the command in a new terminal
# Write-Host "The command 'python manage.py runserver' has been copied to your clipboard."
# Write-Host "Please open a new terminal, paste the command, and run it."
# Read-Host -Prompt "Press Enter to continue after you have started the server"

scripts/import-opml.ps1 "scripts/.data/example.opml"
# Start-Sleep -Seconds 5
# python manage.py makemigrations
# Start-Sleep -Seconds 5
# python manage.py update_episodes
# Start-Sleep -Seconds 5
# python manage.py download_episodes --hours 240