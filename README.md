# Kneecap

Kneecap is an open-source Podcatcher and RSS mirror service built with Django. 

![Animation](https://github.com/user-attachments/assets/6e83ae16-de5d-4f25-938f-65e991e0fe2e)

## Features
- Dashboard for managing feeds and subscriptions
- Web Audio player with advanced playback controls
- RSS feed generation and mirroring
- OPML import/export
- Docker support for easy deployment

## Quickstart

**Note:Unless the SECRET_KEY environment variable is set, the application will not start.**

**Note: Unless the ALLOWED_HOST and SITE_URL environment variables are set with a different port listed, the application will only be accessible at `http://localhost:8000`**

1. pull and run the latest image:

```bash
docker pull ghcr.io/tummyslyunopened/kneecap:canary
docker run -e SECRET_KEY=django-insecure-1234567890 -p 80:8000 ghcr.io/tummyslyunopened/kneecap:canary
```

2. navigate to `http://localhost:8000` in your web browser


### Docker Compose

1. Minimal example
```yml
services:
  kneecap:
    image: ghcr.io/tummyslyunopened/kneecap:canary
    environment:
      SECRET_KEY: $SECRET_KEY
    ports:
      - "80:8000"
```

## Development Setup 

**For local development Django will expect to have environment variables set at kneecap-backend/.dev/.env**

*[uv](https://github.com/astral-sh/uv) is recommended for managing Python environments.*

```bash
git clone https://github.com/tummyslyunopened/kneecap-backend.git
echo "SECRET_KEY=django-insecure-1234567890" > kneecap-backend/.dev/.env
cd kneecap-backend
sh ./entrypoint.sh
```

A powershell entrypoint is also provided:
```powershell
git clone https://github.com/tummyslyunopened/kneecap-backend.git
"SECRET_KEY=django-insecure-1234567890" | Out-File -Encoding utf8 kneecap-backend/.dev/.env
Set-Location kneecap-backend
.\entrypoint.ps1
```

## License
[MIT](LICENSE)
