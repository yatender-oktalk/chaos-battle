# Dockerfile
FROM python:3.11-alpine

# Install build dependencies for psutil
RUN apk add --no-cache gcc musl-dev linux-headers

# Install Python packages
RUN pip install websockets psutil

# Create app directory
WORKDIR /app

# Copy files (fix the filename - note the underscore)
COPY universal_benchmark_with_monitoring.py .
COPY benchmark-configs/config-container.json config.json

# Create results directory
RUN mkdir -p results

CMD ["python", "universal_benchmark_with_monitoring.py", "config.json"]