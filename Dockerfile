FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install uv for faster dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY hep_programming ./hep_programming
COPY hints ./hints
COPY *.md ./

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose the server port
EXPOSE 8080

# Set the TOKEN environment variable (must be provided at runtime)
ENV TOKEN=""

# Run the MCP server
CMD ["uv", "run", "./hep_programming/server.py"]
