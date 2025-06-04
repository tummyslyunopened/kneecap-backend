# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

# Install system dependencies
RUN apk add --no-cache ffmpeg

# Set up virtual environment
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip install --no-deps .

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS runtime

# Install runtime system dependencies
RUN apk add --no-cache ffmpeg

# Copy virtual environment from builder
ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set up application
WORKDIR /app
COPY . .

# Make entrypoint executable and set it as the entrypoint
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
