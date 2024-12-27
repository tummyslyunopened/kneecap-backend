# Delete all migration files
Get-ChildItem -Path . -Filter "*.py" -Recurse | 
    Where-Object { $_.Directory.Name -eq "migrations" -and $_.Name -ne "__init__.py" -and $_.Directory.FullName -notlike "*\.venv*" -and $_.Directory.FullName -notlike "*\activate*" } | 
    ForEach-Object {
        Write-Host "Deleting migration: $($_.FullName)" -ForegroundColor Yellow
        Remove-Item $_.FullName -Force
    }

# Delete SQLite database file
$dbFile = "db.sqlite3"
if (Test-Path $dbFile) {
    Write-Host "Deleting database: $dbFile" -ForegroundColor Red
    Remove-Item $dbFile -Force
}

Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Don't forget to run:" -ForegroundColor Cyan
Write-Host "python manage.py makemigrations" -ForegroundColor White
Write-Host "python manage.py migrate" -ForegroundColor White