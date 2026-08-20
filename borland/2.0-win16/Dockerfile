# Turbo C 2.0 — 16-bit DOS compiler (TCC.EXE under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the Turbo C 2.0
# command-line tree (BIN/INCLUDE/LIB) from the archaic-toolchains/tc20
# preservation repo (sha256-verified codeload — assembled from the
# archive.org `turboc20` floppy disk images) and exposes the `tcc`
# entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/borland:2.0-win16 toolchain/borland/2.0-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:2.0-win16 -c test.c  (ENTRYPOINT is the tcc wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C 2.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C 2.0 (win16, DOSBox) toolchain image"


# Vendored Turbo C 2.0 command-line tree (BIN/INCLUDE/LIB at the tarball top).
RUN curl -sL -o /tmp/tc20.tar.gz \
        "https://codeload.github.com/archaic-toolchains/tc20/tar.gz/refs/heads/main" \
    && echo "2eca4c26c1b30ce2bd7e61573eb9f40096994405fc173c28143f06a93da269d1  /tmp/tc20.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/tc20 \
    && tar xzf /tmp/tc20.tar.gz -C /opt/tc20 --strip-components=1 \
    && rm /tmp/tc20.tar.gz \
    && ls /opt/tc20/BIN/TCC.EXE

# The `tcc` wrapper: translate the POSIX-style argv into the DOSBox TCC
# invocation inside the mounted /work (source staged under an 8.3-safe
# name, object written back to /work).
COPY tc20-run.sh /usr/local/lib/rebrew/tc20-run.sh
RUN chmod +x /usr/local/lib/rebrew/tc20-run.sh

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec /usr/local/lib/rebrew/tc20-run.sh "$@"' \
        > /usr/local/bin/tcc \
    && chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]
