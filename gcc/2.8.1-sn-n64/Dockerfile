# rebrew GCC 2.8.1 SN (N64) — decomp.me "gcc2.8.1sn".
#
# Inherits the shared rebrew/base and installs the pinned `marijnvdwerf/sn64` release assets (the 2.8.1 cc1n64 and asn64).
# decomp.me's recipe is a pipeline with no vendor driver in play, so
# the wrapper runs it and psyq-obj-parser converts the Sony object.
#
# Build:  docker build -t rebrew/gcc:2.8.1-sn-n64 gcc/2.8.1-sn-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.8.1-sn-n64 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.8.1 SN (N64)" \
      org.opencontainers.image.description="GCC 2.8.1 SN (N64) (N64, PE/x86_32 pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-2.8.1-sn \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.8.1-sn/cc1n64.exe \
        "https://github.com/marijnvdwerf/sn64/releases/download/1%2C0%2C0%2C2/cc1n64.exe" \
    && echo "d90df1028c46d826e37146dbcc3e3385f78c59e05a9ddd952daa94c9ad379d9c  /opt/gcc-2.8.1-sn/cc1n64.exe" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.8.1-sn/asn64.exe \
        "https://github.com/marijnvdwerf/sn64/releases/download/1%2C0%2C0%2C2/asn64.exe" \
    && echo "53e3a9f8b7b9a06c8f5a781f01074441df3469e6bbe2df5438ba4e2d8fcf3819  /opt/gcc-2.8.1-sn/asn64.exe" | sha256sum -c - \
    && rm -rf /tmp/tools && chmod +x /opt/gcc-2.8.1-sn/*.exe

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.8.1-sn \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.8.1-sn/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENV REBREW_RUNNER=wibo

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
