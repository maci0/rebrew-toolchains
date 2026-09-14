# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-9.0.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 9.0.0 (Switch)" \
      org.opencontainers.image.description="Clang 9.0.0 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev binutils \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/clang-9.0.0/lib

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz" \
    && echo "a23b082b30c128c9831dbdd96edad26b43f56624d0ad0ea9edec506f5385038d  /tmp/clang.tar.xz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/libtinfo5.deb \
        "https://deb.debian.org/debian/pool/main/n/ncurses/libtinfo5_6.4-4_amd64.deb" \
    && echo "dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a  /tmp/libtinfo5.deb" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-9.0.0 /tmp/tinfo5 \
    && tar xJf /tmp/clang.tar.xz --strip-components=1 -C /opt/clang-9.0.0 \
    && cd /tmp/tinfo5 \
    && ar x /tmp/libtinfo5.deb data.tar.xz \
    && tar xJf data.tar.xz \
    && cp lib/x86_64-linux-gnu/libtinfo.so.5* /opt/clang-9.0.0/lib/ \
    && rm -rf /tmp/tinfo5 /tmp/clang.tar.xz /tmp/libtinfo5.deb \
    && LD_LIBRARY_PATH=/opt/clang-9.0.0/lib /opt/clang-9.0.0/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
