# agbccpp — GBA decomp C++ compiler (notyourav/agbcc `cp` fork, tag-pinned).
#
# pret/agbcc dropped the C++ frontend; decomp.me sources agbccpp from the
# notyourav/agbcc fork (tag `cp`), whose release ships the `agbcp` C++
# driver alongside the agbcc binaries.  Inherits the shared rebrew/base;
# native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/agbccpp:gba agbccpp/gba
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/agbccpp:gba -quiet -c t.cpp -o t.o

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbccpp (GBA)" \
      org.opencontainers.image.description="agbccpp (notyourav cp fork, GBA, native x86_64) toolchain image"

# Tarball root IS the tool (bin/, include/, lib/) — extract in place.
# The release asset is rebuilt on pushes to the `cp` branch; re-pin on drift.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbccpp.tar.gz \
        "https://github.com/notyourav/agbcc/releases/download/cp/agbcc.tar.gz" \
    && echo "05a30f03ee916563bba29efdc9da64c47909892aa878002cf07e8e7ae5bd32f5  /tmp/agbccpp.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/agbccpp \
    && tar xzf /tmp/agbccpp.tar.gz -C /opt/agbccpp \
    && rm /tmp/agbccpp.tar.gz \
    && chmod +x /opt/agbccpp/bin/agbcp \
    && ls /opt/agbccpp/bin/agbcp

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/agbccpp/bin/agbcp "$@"' \
        > /usr/local/bin/agbccpp \
    && chmod +x /usr/local/bin/agbccpp

ENTRYPOINT ["/usr/local/bin/agbccpp"]

USER rebrew
