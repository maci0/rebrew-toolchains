# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-5.3-cxx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 C++ (N64, qemu-irix)" \
      org.opencontainers.image.description="IDO 5.3 C++ (SGI MIPS, N64, IRIX binaries under qemu-irix) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido.tar.xz \
        "https://github.com/LLONSIT/qemu-irix-helpers/raw/d577d1654ca4b57585af59849cb067c0148874d7/qemu/ido5.3_c++.tar.xz" \
    && echo "851426c63ffb0688c702793113c2d9aa3c703c7a4e9d4240fc99d1862f79e4b9  /tmp/ido.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/ido-5.3-c++ \
    && tar xJf /tmp/ido.tar.xz -C /opt/ido-5.3-c++ \
    && rm /tmp/ido.tar.xz \
    && chmod +x /opt/ido-5.3-c++/usr/bin/qemu-irix \
    && ls /opt/ido-5.3-c++/usr/lib/CC

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
