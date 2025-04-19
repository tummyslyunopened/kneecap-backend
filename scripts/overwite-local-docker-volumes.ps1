docker run -d -v kneecap_db:/db/ -v kneecap_static:/static/ -v kneecap_media:/media/ kneecap/server:0.0
$containerId = $(docker ps -lq)

# // Clear the static and media directories
docker exec ${containerId} sh -c "rm -rf /static/*"
docker exec ${containerId} sh -c "rm -rf /media/*"

# // Recreate the static and media directories
docker exec ${containerId} sh -c "mkdir -p /static /media"

docker cp ../db.sqlite3 ${containerId}:/db/
Get-ChildItem -Path ../static | ForEach-Object {
    docker cp $_.FullName ${containerId}:/static/
}
Get-ChildItem -Path ../media | ForEach-Object {
    docker cp $_.FullName ${containerId}:/media/
}
docker rm -f $containerId