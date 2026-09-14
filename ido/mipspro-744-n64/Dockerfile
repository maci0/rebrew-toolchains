# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-mipspro-744

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MIPSpro 7.4.4 (N64, qemu-irix)" \
      org.opencontainers.image.description="MIPSpro 7.4.4 (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/mipspro7.4.4.tar.xz" \
    && echo "df33be0d9605b00b44070e567121fc00283a9b1f97763403f0898d2216028d24  /tmp/ido.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/ido-mipspro-744 \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-mipspro-744 \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-mipspro-744/usr/bin/qemu-irix \
    && ls /opt/ido-mipspro-744/usr/lib/driver

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
