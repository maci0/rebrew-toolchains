# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-6.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 6.0 (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 6.0 (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido6.0.tar.xz" \
    && echo "c56d4be020bdaf76310ceec455ebc0d443fb7a46c740491f74898b04f6a60356  /tmp/ido.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/ido-6.0 \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-6.0 \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-6.0/usr/bin/qemu-irix \
    && /opt/ido-6.0/usr/bin/qemu-irix --version 2>&1 | head -1 || true

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
