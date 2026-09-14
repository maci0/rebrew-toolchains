# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-18.1.8

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 18.1.8 (ELF/x86_64, native)" \
      org.opencontainers.image.description="Clang 18.1.8 (ELF/x86_64, native, LLVM release build) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev libtinfo5 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.8/clang+llvm-18.1.8-x86_64-linux-gnu-ubuntu-18.04.tar.xz" \
    && echo "54ec30358afcc9fb8aa74307db3046f5187f9fb89fb37064cdde906e062ebf36  /tmp/clang.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-18.1.8 \
    && tar xJf /tmp/clang.tar.xz --strip-components=1 -C /opt/clang-18.1.8 \
    && rm /tmp/clang.tar.xz \
    && /opt/clang-18.1.8/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
