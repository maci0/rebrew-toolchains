# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-4.0.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 4.0.1 (Switch)" \
      org.opencontainers.image.description="Clang 4.0.1 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH="/opt/clang-4.0.1/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/4.0.1/clang+llvm-4.0.1-x86_64-linux-gnu-debian8.tar.xz" \
    && echo "ca48a4def4cbc9dd6af3f46ce1dc2bd903d26c7ad51387f57884ad1eaa58e42f  /tmp/clang.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-4.0.1 \
    && tar xJf /tmp/clang.tar.xz --strip-components=1 -C /opt/clang-4.0.1 \
    && rm /tmp/clang.tar.xz \
    && ln -s "$(ldconfig -p \
    && LD_LIBRARY_PATH=/opt/clang-4.0.1/lib /opt/clang-4.0.1/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
