# agbcc — GBA decomp compiler (pret/agbcc_arm release build).
#
# Inherits the shared rebrew/base; this image installs the pinned pret/agbcc_arm
# release asset (bin/, include/, lib/ at the tarball root: agbcc, old_agbcc,
# agbcc_arm + libgcc.a/libc.a) and exposes the `agbcc_arm` front end as the
# entrypoint.  Native ELF — no wine/DOSBox.
#
# Build:  docker build -t rebrew/agbcc_arm:gba agbcc/gba
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/agbcc:arm-gba -o - t.c > t.s
#
# cc1-style front end: prints assembly (feed it preprocessed input) and rejects
# the `-quiet`/`-c` spelling other compilers here use.

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbcc (ARM mode, GBA)" \
      org.opencontainers.image.description="agbcc ARM-mode front end (pret, GBA, native x86_64) toolchain image"

# Tarball root IS the tool (bin/, include/, lib/) — extract in place.
# NOTE: the upstream `release` tag is rebuilt on every push to pret/agbcc_arm
# master; the pin below hashes the asset current at image-authoring time
# (moving tag — re-pin on drift, like the Watcom 16-bit snapshot).
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbcc.tar.gz \
        "https://github.com/pret/agbcc/releases/download/release/agbcc.tar.gz" \
    && echo "bcf0197e3e27d8e08506a142e25fa68ea7f6679a98347a6406804eb3f9ff4d29  /tmp/agbcc.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/agbcc-agbcc_arm \
    && tar xzf /tmp/agbcc.tar.gz -C /opt/agbcc-agbcc_arm \
    && rm /tmp/agbcc.tar.gz \
    && chmod +x /opt/agbcc-agbcc_arm/bin/agbcc_arm \
    && ls /opt/agbcc-agbcc_arm/bin/agbcc_arm

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_exec /opt/agbcc-agbcc_arm/bin/agbcc_arm "$@"' \
        > /usr/local/bin/agbcc_arm \
    && chmod +x /usr/local/bin/agbcc_arm

ENTRYPOINT ["/usr/local/bin/agbcc_arm"]

USER rebrew
