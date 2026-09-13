# rebrew GCC 2.7.2 SNEW (N64) — decomp.me "gcc2.7.2snew".
#
# Inherits the shared rebrew/base and installs the decompals SN64-gcc 2.7.2-970404 Linux tree and RocketRet's modern-asn64.py assembler script.
# The tree has no assembler of its own: decomp.me assembles through the
# Python script, which drives GNU as (binutils-mips-linux-gnu here).
#
# Build:  docker build -t rebrew/gcc:2.7.2-snew-n64 gcc/2.7.2-snew-n64
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/gcc:2.7.2-snew-n64 -c f.c -o f.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 2.7.2 SNEW (N64)" \
      org.opencontainers.image.description="GCC 2.7.2 SNEW (SN64, N64, native x86_64 + modern-asn64.py) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 binutils-mips-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/gcc-2.7.2-snew /tmp/tools \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/sn64-new.tar.gz \
        "https://github.com/decompals/SN64-gcc/releases/download/gcc-2.7.2-970404/SN64-gcc-2.7.2-970404-linux.tar.gz" \
    && echo "60abe17c2562f5ae28444fe4f783fa8217d84b73e59e29cf39c41f7551d968f4  /tmp/tools/sn64-new.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/tools/sn64-new.tar.gz -C /opt/gcc-2.7.2-snew \
    && curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-2.7.2-snew/modern-asn64.py \
        "https://github.com/RocketRet/modern-asn64/releases/download/main-release/modern-asn64.py" \
    && echo "7e6815e2c2c0ae0b4581ace1c5adab3d1d567f0fc729f674fc52bdd77e2240bc  /opt/gcc-2.7.2-snew/modern-asn64.py" | sha256sum -c - \
    && rm -rf /tmp/tools && chmod +x /opt/gcc-2.7.2-snew/*.py /opt/gcc-2.7.2-snew/cc1

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
