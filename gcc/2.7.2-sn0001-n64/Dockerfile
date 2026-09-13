# rebrew GCC 2.7.2 SN0001 (N64) — decomp.me "gcc2.7.2sn0001".
#
# Inherits the shared rebrew/base and installs the decompme/compilers `n64_sn272_0001` tarball (cc1n64.exe, cc1pln64.exe, asn64.exe).
# decomp.me's recipe is a pipeline with no vendor driver in play, so
# the wrapper runs it and psyq-obj-parser converts the Sony object.
#
# Build:  docker build -t rebrew/gcc:2.7.2-sn0001-n64 gcc/2.7.2-sn0001-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-sn0001-n64 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 SN0001 (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 SN0001 (N64) (N64, PE/x86_32 pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-2.7.2-sn0001 /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/n64_sn272_0001.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/n64_sn272_0001.tar.gz" \
    && echo "17c57ccd5f2305fe5445c576d4cc2c1fea681dd78b29dd3d1f15c5ca0fdf2cea  /tmp/tools/n64_sn272_0001.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/tools/n64_sn272_0001.tar.gz -C /opt/gcc-2.7.2-sn0001 \
    && rm -rf /tmp/tools && chmod +x /opt/gcc-2.7.2-sn0001/*.exe

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.7.2-sn0001 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.7.2-sn0001/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENV REBREW_RUNNER=wibo

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
