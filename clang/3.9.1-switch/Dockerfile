# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-3.9.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 3.9.1 (Switch)" \
      org.opencontainers.image.description="Clang 3.9.1 (LLVM prebuilt, native x86_64, Switch decomp) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev binutils \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/clang-3.9.1/lib

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://releases.llvm.org/3.9.1/clang+llvm-3.9.1-x86_64-linux-gnu-debian8.tar.xz" \
    && echo "dbe2ad98cd9c2b718fdfb5dc72dcf9cfb91009d05a5b2b37457cccc958559b2a  /tmp/clang.tar.xz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/libtinfo5.deb \
        "https://deb.debian.org/debian/pool/main/n/ncurses/libtinfo5_6.4-4_amd64.deb" \
    && echo "dd347f794e651039e7b4c391f86c674fed7f415b3dca6b0937beb0d470f09c1a  /tmp/libtinfo5.deb" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-3.9.1 /tmp/tinfo5 \
    && tar xJf /tmp/clang.tar.xz --strip-components=1 -C /opt/clang-3.9.1 \
    && cd /tmp/tinfo5 \
    && ar x /tmp/libtinfo5.deb data.tar.xz \
    && tar xJf data.tar.xz \
    && cp lib/x86_64-linux-gnu/libtinfo.so.5* /opt/clang-3.9.1/lib/ \
    && rm -rf /tmp/tinfo5 /tmp/clang.tar.xz /tmp/libtinfo5.deb \
    && LD_LIBRARY_PATH=/opt/clang-3.9.1/lib /opt/clang-3.9.1/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
