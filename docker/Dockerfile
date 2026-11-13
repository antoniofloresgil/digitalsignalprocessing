# One Linux/amd64 environment for three jobs: rendering the book (HTML + PDF),
# running the chapter code in JupyterLab, and the VS Code dev container.
# Base image and Quarto are pinned by digest/hash; Python packages are pinned
# in docker/requirements.txt. Ubuntu packages follow the 24.04 archive.
FROM ubuntu:24.04@sha256:84e77dee7d1bc93fb029a45e3c6cb9d8aa4831ccfcc7103d36e876938d28895b

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl git make \
       python3 python3-venv \
       texlive-xetex texlive-latex-recommended texlive-latex-extra \
       texlive-fonts-recommended texlive-fonts-extra texlive-plain-generic lmodern fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

ARG QUARTO_VERSION=1.10.19
ARG QUARTO_SHA256=7f0c4769e7f0e55f50d922f44b18db5118fb388d2b8fd27291fe1f8beafb43eb
RUN curl --fail --location --retry 3 \
      "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
      --output /tmp/quarto.deb \
    && echo "${QUARTO_SHA256}  /tmp/quarto.deb" | sha256sum --check \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

COPY docker/requirements.txt /opt/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --requirement /opt/requirements.txt

ENV PATH=/opt/venv/bin:$PATH \
    QUARTO_PYTHON=/opt/venv/bin/python \
    MPLCONFIGDIR=/tmp/matplotlib \
    XDG_CACHE_HOME=/tmp/cache \
    TEXMFVAR=/tmp/texmf-var

WORKDIR /work
CMD ["quarto", "render"]
