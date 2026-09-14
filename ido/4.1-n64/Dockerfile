# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-4.1

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 4.1 (N64, qemu-irix-4.0)" \
      org.opencontainers.image.description="IDO 4.1 (SGI MIPS, N64 little-endian, IRIX binaries under qemu-irix-4.0) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 python3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido41.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ido4.1.tar.gz" \
    && echo "16008087602fe1a39cdd7880a3c6987891ddb594cce4416670f2e96456e9b4d4  /tmp/ido41.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/ido-4.1 \
    && tar xzf /tmp/ido41.tar.gz -C /opt/ido-4.1 \
    && rm /tmp/ido41.tar.gz \
    && chmod +x /opt/ido-4.1/usr/bin/qemu-irix-4.0 \
    && /opt/ido-4.1/usr/bin/qemu-irix-4.0 --version 2>&1 | head -1 || true

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
