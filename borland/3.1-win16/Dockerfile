# Turbo C++ 3.1 — 16-bit DOS compiler (TCC.EXE under DOSBox).
#
# Inherits the shared rebrew/base; this image adds the Turbo C++ 3.1
# command-line tree (BIN/INCLUDE/LIB) from the committed tc31.tar.xz
# (vendored from the archive.org `turboc3.1_202112` item, sha256-verified)
# and exposes the `tcc` entrypoint wrapper.  Fully self-contained: no host
# files, no downloads.
#
# Build:  docker build -t rebrew/borland:3.1-win16 toolchain/borland/3.1-win16
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/borland:3.1-win16 -c test.c  (ENTRYPOINT is the tcc wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C++ 3.1 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C++ 3.1 (win16, DOSBox) toolchain image"


# Vendored Turbo C++ 3.1 command-line tree (BIN/INCLUDE/LIB at the tarball top).
COPY tc31.tar.xz /tmp/tc31.tar.xz
RUN mkdir -p /opt/tc31 \
    && tar xJf /tmp/tc31.tar.xz -C /opt/tc31 \
    && rm /tmp/tc31.tar.xz \
    && ls /opt/tc31/BIN/TCC.EXE

# The `tcc` wrapper: translate the POSIX-style argv into the DOSBox TCC
# invocation inside the mounted /work (source staged under an 8.3-safe
# name, object written back to /work).
COPY tc16-run.sh /usr/local/lib/rebrew/tc16-run.sh
RUN chmod +x /usr/local/lib/rebrew/tc16-run.sh

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec /usr/local/lib/rebrew/tc16-run.sh "$@"' \
        > /usr/local/bin/tcc \
    && chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]
