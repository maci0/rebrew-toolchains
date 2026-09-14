# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-5.3-irix

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 IRIX originals (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 5.3 (SGI MIPS, N64, original IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ido-irix-5.3 /tmp/ido && curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido/ssb.tar \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ssb_ido5.3.tar" \
    && echo "a8a5bfa1713cc63c157ed4d61d0fb19f2d2ab10612fd9df2ceeb1de517cda4d4  /tmp/ido/ssb.tar" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido_root.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido_root.tar.xz" \
    && echo "d0d8a0deb1508fb1d3e91d5eaaded16a267af0be8e98aac7a104ba1bf4f677fb  /tmp/ido_root.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && tar xf /tmp/ido/ssb.tar -C /opt/ido-irix-5.3 \
    && rm -rf /tmp/ido \
    && ls /opt/ido-irix-5.3/usr/lib/driver \
    && tar xJf /tmp/ido_root.tar.xz -C /tmp \
    && cp /tmp/ido_root/usr/bin/qemu-irix /opt/ido-irix-5.3/usr/bin/qemu-irix \
    && rm -rf /tmp/ido_root.tar.xz /tmp/ido_root \
    && chmod +x /opt/ido-irix-5.3/usr/bin/qemu-irix \
    && /opt/ido-irix-5.3/usr/bin/qemu-irix --version

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
