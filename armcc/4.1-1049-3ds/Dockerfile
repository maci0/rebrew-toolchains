# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: armcc-4.1-1049

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ARMCC 4.1-1049 (3DS)" \
      org.opencontainers.image.description="ARMCC 4.1-1049 (CodeWarrior 3DS, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://github.com/decompme/compilers/releases/download/compilers/armcc.zip?2026-03-04" \
    && echo "bda0cea5b13a9c3f08322fa76f9f9dcda59bda290f57f1a06e05cd80044fafdb  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/armcc-4.1-1049 \
    && unzip -q /tmp/compilers.zip '4.1/b1049/*' -d /tmp/x \
    && cp -a /tmp/x/4.1/b1049/. /opt/armcc-4.1-1049/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/armcc-4.1-1049/bin/armcc.exe

COPY armcc-wrapper.sh /usr/local/bin/armcc
RUN chmod +x /usr/local/bin/armcc

ENTRYPOINT ["/usr/local/bin/armcc"]

USER rebrew
