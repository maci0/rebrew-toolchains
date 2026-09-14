# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-16.0.4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 16.0.4 (ELF/x86_64, native)" \
      org.opencontainers.image.description="Clang 16.0.4 (ELF/x86_64, native, LLVM release build) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-16.0.4/clang+llvm-16.0.4-x86_64-linux-gnu-ubuntu-22.04.tar.xz" \
    && echo "fd464333bd55b482eb7385f2f4e18248eb43129a3cda4c0920ad9ac3c12bdacf  /tmp/clang.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-16.0.4 \
    && tar xJf /tmp/clang.tar.xz --strip-components=1 -C /opt/clang-16.0.4 \
    && rm /tmp/clang.tar.xz \
    && /opt/clang-16.0.4/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
