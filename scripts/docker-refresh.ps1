docker ps -aq | ForEach-Object { docker rm $_ }
docker rmi -f $(docker images -aq)
docker build .
