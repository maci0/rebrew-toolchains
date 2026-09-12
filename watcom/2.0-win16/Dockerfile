# Open Watcom 2.0 (C) — x86 16-bit codegen compiler (native Linux).
#
# Inherits the shared rebrew/base; this image downloads the pinned Open Watcom
# 2.0 snapshot (ow-snapshot.tar.xz — the official self-extracting installer
# SIGFPEs on modern glibc, known issue) and uses wcc, the 16-bit compiler, as
# the entrypoint (wcc386 in the sibling 2.0-win32 image is the 32-bit one).
# Fully self-contained: no host files.
#
# The snapshot is pinned to the dated 2026-09-01-Build release rather than the
# moving Last-CI-build tag: Last-CI-build is republished on every CI run, and
# the sha256 sources.json recorded for it earlier (5c87c104…) no longer
# resolves upstream (the asset hashes to 57af2579… as of 2026-09-12).  A dated
# release asset stays valid, so this image rebuilds reproducibly.
#
# Build:  docker build -t rebrew/watcom:2.0-win16 watcom/2.0-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:2.0-win16 -fo=out.obj f.c  (ENTRYPOINT is wcc)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Open Watcom 2.0 (win16, native)" \
      org.opencontainers.image.description="Open Watcom 2.0 (win16, native) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ow.tar.xz \
        "https://github.com/open-watcom/open-watcom-v2/releases/download/2026-09-01-Build/ow-snapshot.tar.xz" \
    && echo "bac354f3c75ffa49ff8d70a44e475de7e7c1823fff04b80c14787bd0792c9bdf  /tmp/ow.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/watcom \
    && tar xJf /tmp/ow.tar.xz -C /opt/watcom --strip-components=1 \
    && rm /tmp/ow.tar.xz \
    && ls /opt/watcom/binl/wcc

# wcc (16-bit x86, native) — rebrew's entrypoint.  Emits 16-bit OMF object
# modules by default; the OMF parser is the enabling follow-up.  The wrapper
# runs it under the shared watchdog (REBREW_RUNNER_TIMEOUT) so a hung compile
# fails loudly like the wine/DOSBox entrypoints.
ENV WATCOM=/opt/watcom \
    INCLUDE=/opt/watcom/h \
    PATH=/opt/watcom/binl:$PATH

COPY wcc-wrapper.sh /usr/local/bin/wcc
RUN chmod +x /usr/local/bin/wcc

ENTRYPOINT ["/usr/local/bin/wcc"]

# Runtime drops back to the base image's non-root user.
USER rebrew
