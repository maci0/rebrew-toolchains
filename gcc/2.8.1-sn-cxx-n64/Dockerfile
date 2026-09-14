# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-2.8.1-sn-cxx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.8.1 SN C++ (N64)" \
      org.opencontainers.image.description="GCC 2.8.1 SN C++ (N64, PE/x86_32 pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.8.1-sn-cxx-n64/cc1n64.exe \
        "https://github.com/marijnvdwerf/sn64/releases/download/1%2C0%2C0%2C2/cc1n64.exe" \
    && echo "d90df1028c46d826e37146dbcc3e3385f78c59e05a9ddd952daa94c9ad379d9c  /opt/gcc-2.8.1-sn-cxx-n64/cc1n64.exe" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.8.1-sn-cxx-n64/cc1pln64.exe \
        "https://github.com/marijnvdwerf/sn64/releases/download/1%2C0%2C0%2C2/cc1pln64.exe" \
    && echo "85e3e9fa05640af67115279a992a616a1a1fec8cf56b2e58191196fbbc51853a  /opt/gcc-2.8.1-sn-cxx-n64/cc1pln64.exe" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.8.1-sn-cxx-n64/asn64.exe \
        "https://github.com/marijnvdwerf/sn64/releases/download/1%2C0%2C0%2C2/asn64.exe" \
    && echo "53e3a9f8b7b9a06c8f5a781f01074441df3469e6bbe2df5438ba4e2d8fcf3819  /opt/gcc-2.8.1-sn-cxx-n64/asn64.exe" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-2.8.1-sn-cxx-n64 \
    && chmod +x /opt/gcc-2.8.1-sn-cxx-n64/*.exe \
    && tar xzf /tmp/parser.tar.gz -C /opt/gcc-2.8.1-sn-cxx-n64 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/gcc-2.8.1-sn-cxx-n64/psyq-obj-parser \
    && chmod +x /usr/local/bin/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
