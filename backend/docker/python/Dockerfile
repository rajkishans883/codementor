FROM python:3.11-slim

# Non-root user for safety
RUN useradd -m runner
USER runner
WORKDIR /home/runner

# Default command
CMD ["python3"]