Remove-Item -Path .\random.mp4 -ErrorAction SilentlyContinue
$themes = Get-ChildItem -Path .\* | Where-Object { $_.Name -ne 'random.mp4' }
$rand = Get-Random -InputObject $themes
Copy-Item -Path $rand.FullName -Destination .\random.mp4 -Force
Write-Host "Random episode selected: $($rand.Name) -> random.mp4"
