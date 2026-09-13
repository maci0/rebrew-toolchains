# rebrew GCC 2.7.2 SN0004 (N64) — decomp.me "gcc2.7.2sn0004".
#
# Inherits the shared rebrew/base and installs the pcsx-redux n64 release assets (cc1n64.exe and asn64.exe; the latter is installed under that name).
# decomp.me's recipe is a pipeline with no vendor driver in play, so
# the wrapper runs it and psyq-obj-parser converts the Sony object.
#
# Build:  docker build -t rebrew/gcc:2.7.2-sn0004-n64 gcc/2.7.2-sn0004-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-sn0004-n64 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 SN0004 (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 SN0004 (N64) (N64, PE/x86_32 pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-2.7.2-sn0004 \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.7.2-sn0004/cc1n64.exe \
        "https://github.com/Mr-Wiseguy/pcsx-redux/releases/download/n64/cc1n64.exe" \
    && echo "17b0d9dc6a80b2aaec90f912bb442321ec8bc5cecaf7071f5bd187e1d6525d49  /opt/gcc-2.7.2-sn0004/cc1n64.exe" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.7.2-sn0004/asn64.exe \
        "https://github.com/Mr-Wiseguy/pcsx-redux/releases/download/n64/asn64.exe" \
    && echo "1e04e1195f6504fe711c3db67ad94eb50d47f2a0f21e87dbbe20cbac4d83db39  /opt/gcc-2.7.2-sn0004/asn64.exe" | sha256sum -c - \
    && rm -rf /tmp/tools && chmod +x /opt/gcc-2.7.2-sn0004/*.exe

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.7.2-sn0004 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.7.2-sn0004/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENV REBREW_RUNNER=wibo

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
