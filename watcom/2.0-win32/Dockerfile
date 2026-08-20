# Open Watcom 2.0 (C) — x86 32-bit codegen compiler (native Linux).
#
# Inherits the shared rebrew/base; this image downloads the Open Watcom 2.0
# CI snapshot (ow-snapshot.tar.xz — the official self-extracting installer
# SIGFPEs on modern glibc, known issue), sha256-pinned so the moving
# Last-CI-build tag is deterministic, and uses wcc386 as the entrypoint.
# Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/watcom:2.0-win32 toolchain/watcom/2.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:2.0-win32 -fo=out.o f.c  (ENTRYPOINT is wcc386)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Open Watcom 2.0 (win32, native)" \
      org.opencontainers.image.description="Open Watcom 2.0 (win32, native) toolchain image"


RUN curl -sL -o /tmp/ow.tar.xz \
        "https://github.com/open-watcom/open-watcom-v2/releases/download/Last-CI-build/ow-snapshot.tar.xz" \
    && echo "99e494d9a3871f58a6398268e8f04003affa73421ca5fb49e3815a8ef1bb7b1f  /tmp/ow.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/watcom \
    && tar xJf /tmp/ow.tar.xz -C /opt/watcom --strip-components=1 \
    && rm /tmp/ow.tar.xz \
    && ls /opt/watcom/binl/wcc386

# wcc386 (32-bit x86, native) — rebrew's entrypoint.  Emits OMF objects by
# default (8086 relocatable); the OMF parser is the enabling follow-up.
ENV WATCOM=/opt/watcom \
    INCLUDE=/opt/watcom/h \
    PATH=/opt/watcom/binl:$PATH

ENTRYPOINT ["/opt/watcom/binl/wcc386"]
