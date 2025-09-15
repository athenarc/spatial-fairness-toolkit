FROM continuumio/miniconda3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    git \
    libgdal-dev \
    python3-dev \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

COPY . .

RUN conda env create -f environment.yml

# Add Conda to PATH for non-login shells
ENV PATH /opt/conda/envs/spatial-bias-env/bin:$PATH

# Expose the port
EXPOSE 8000

# Add startup script
COPY start.sh /start.sh
RUN dos2unix /start.sh && chmod +x /start.sh

# Use the script as entrypoint
ENTRYPOINT ["/start.sh"]
