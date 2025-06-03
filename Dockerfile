FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    pkg-config \
    libffi-dev \
    libssl-dev \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source with proper environment
RUN cd /tmp && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr --build=x86_64-linux-gnu && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/ta-lib*

# Set environment variables for TA-Lib Python package
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in stages to isolate issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install core dependencies first
RUN pip install --no-cache-dir \
    numpy>=1.24.0 \
    pandas>=2.0.0 \
    scipy>=1.11.0

# Debug: Check TA-Lib installation
RUN ls -la /usr/lib/libta_lib* || echo "TA-Lib libraries not found in /usr/lib"
RUN ls -la /usr/include/ta-lib/ || echo "TA-Lib headers not found in /usr/include"
RUN pkg-config --exists ta-lib && echo "TA-Lib pkg-config found" || echo "TA-Lib pkg-config missing"

# Install TA-Lib Python package with environment variables and fallback
RUN TA_LIBRARY_PATH=/usr/lib TA_INCLUDE_PATH=/usr/include pip install --no-cache-dir TA-Lib>=0.4.25 || \
    (echo "TA-Lib installation failed, system will use fallback indicators" && \
     echo "Enhanced technical analysis will degrade gracefully to custom implementations")

# Install PyTorch (CPU version for Railway compatibility)
RUN pip install --no-cache-dir \
    torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables for Railway
ENV PYTHONPATH=/app
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["python", "modular_production_main.py"]