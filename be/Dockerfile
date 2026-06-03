# Use python ver 3.12 base image
# slim = stripped down version, bookworm = stable debian version
FROM python:3.12-slim-bookworm

# Goes to the app directory
WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependencies requirements
COPY pyproject.toml uv.lock ./

# Install app dependencies
RUN uv sync --frozen --no-dev

# Copy the rest of our app into the container
COPY . .

# Set port environment variable
ENV PORT=8080
# Expose the port so our computer can access it
EXPOSE 8080

# Run healthcheck, docker would restart if fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD sh -c "python -c \"import os, requests; requests.get('http://localhost:' + os.getenv('PORT', '8080') + '/health')\""

# Run the app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]