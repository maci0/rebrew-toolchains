# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.7.2-sn0004

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

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.7.2-sn0004/cc1n64.exe \
        "https://github.com/Mr-Wiseguy/pcsx-redux/releases/download/n64/cc1n64.exe" \
    && echo "17b0d9dc6a80b2aaec90f912bb442321ec8bc5cecaf7071f5bd187e1d6525d49  /opt/gcc-2.7.2-sn0004/cc1n64.exe" | sha256sum -c -

RUN mkdir -p /opt/gcc-2.7.2-sn0004 && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.7.2-sn0004/asn64.exe \
        "https://github.com/Mr-Wiseguy/pcsx-redux/releases/download/n64/asn64.exe" \
    && echo "1e04e1195f6504fe711c3db67ad94eb50d47f2a0f21e87dbbe20cbac4d83db39  /opt/gcc-2.7.2-sn0004/asn64.exe" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/tools \
    && chmod +x /opt/gcc-2.7.2-sn0004/*.exe \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.7.2-sn0004 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.7.2-sn0004/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
