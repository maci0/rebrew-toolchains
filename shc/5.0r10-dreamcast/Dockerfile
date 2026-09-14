# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: shc-5.0r10

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew SHC 5.0r10 (Dreamcast)" \
      org.opencontainers.image.description="SHC 5.0r10 (Hitachi SuperH, Dreamcast, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/shc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/shc-v5.0r10.tar.gz" \
    && echo "1932570b2f751c26b18e5c7f3a7f9ab453aa05a13d1c06787e60fba7711d0016  /tmp/shc.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/shc-5.0r10/rof2elf.py \
        "https://gist.githubusercontent.com/Mc-muffin/c2d3f30e50c5c5749f994973441c503a/raw/18fbf1a19bd720d02774ed634b00b0508eaf474c/rof2elf.py" \
    && echo "f5a52b69b619e206172da4dc74182ecc97eeac5dcfcf5466c537af5ea6310821  /opt/shc-5.0r10/rof2elf.py" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/shc-5.0r10 \
    && tar xzf /tmp/shc.tar.gz -C /opt/shc-5.0r10 \
    && rm /tmp/shc.tar.gz \
    && chmod +x /opt/shc-5.0r10/rof2elf.py /opt/shc-5.0r10/bin/* \
    && ls /opt/shc-5.0r10/bin/shc.exe

COPY shc-wrapper.sh /usr/local/bin/shc
RUN chmod +x /usr/local/bin/shc

ENTRYPOINT ["/usr/local/bin/shc"]

USER rebrew
