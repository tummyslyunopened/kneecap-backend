$release = gh api  -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"   /repos/ytdl-org/ytdl-nightly/releases/latest | ConvertFrom-Json
$asset = $release.assets | Where-Object {$_.name -eq "youtube-dl.exe"}
Write-Host $asset.browser_download_url
curl -L $asset.browser_download_url -o .venv/Scripts/youtube-dl.exe
