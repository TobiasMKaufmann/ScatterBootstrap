FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    curl \
    vim \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

# Copy the project and build + install the package (compiles all C extensions).
COPY . .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .[dev]

# Sanity check: the package and every compiled model import correctly.
RUN python -c "import scatterbootstrap as sb; print('models:', sb.list_form_factor_models())"

CMD ["bash"]