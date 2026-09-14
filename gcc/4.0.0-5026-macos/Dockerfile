# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-4.0.0-5026

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Apple GCC 4.0.0 build 5026 (macOS)" \
      org.opencontainers.image.description="powerpc-apple-darwin (Apple GCC 4.0.0 build 5026) cross compiler (native x86_64) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 binutils-powerpc-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/gcc-5026.tar.gz \
        "https://github.com/ChrisNonyminus/powerpc-darwin-cross/releases/download/initial/gcc-5026.tar.gz" \
    && echo "74c5c4fb729544ebeb376de8eaa6126edfa7e3c55fa01f071e1a6e597e9a0896  /tmp/tools/gcc-5026.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/gcc-4.0.0-5026/convert_gas_syntax.py \
        "https://gist.githubusercontent.com/ChrisNonyminus/ec53837b151a65e4233fa53604de4549/raw/d7c6fc639310b938fa519e68a8f8d4909acba2ad/convert_gas_syntax.py" \
    && echo "8ad067bedef54c526774e6453f55ef7a2bedc93604bd7640a6a8a1cc64b3cda0  /opt/gcc-4.0.0-5026/convert_gas_syntax.py" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-4.0.0-5026 /tmp/tools \
    && tar xzf /tmp/tools/gcc-5026.tar.gz -C /opt/gcc-4.0.0-5026 \
    && rm -rf /tmp/tools \
    && chmod +x /opt/gcc-4.0.0-5026/cc1 /opt/gcc-4.0.0-5026/convert_gas_syntax.py \
    && chmod +x /usr/local/bin/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
