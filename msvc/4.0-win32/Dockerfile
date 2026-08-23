# MSVC 4.0 — 32-bit PE compiler under wine (archaic-toolchains/msvc400).
#
# Inherits the shared rebrew/base; this image adds the MSVC 4.0
# command-line toolchain (archaic-toolchains/msvc400 repo tarball, sha256-pinned)
# and the `cl` entrypoint wrapper.  Fully self-contained: no host files.
# Note the tree is all-caps (BIN/INCLUDE/LIB) — wine handles the case
# fine; only the wrapper path must match.
#
# Build:  docker build -t rebrew/msvc:4.0-win32 msvc/4.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:4.0-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.0 (win32, wine) toolchain image"

# MSVC 4.0 command-line toolchain — archaic-toolchains/msvc400 repo tarball
# (sha256-verified; byte-identical to the itsmattkc/MSVC400 tree this image
# previously built from).
RUN curl -sL -o /tmp/msvc400.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc400/tar.gz/refs/heads/main" \
    && echo "4996b91a8e075715238817ad567994b8dbf830d25d2c6e0fefe7adacc5b4ddec  /tmp/msvc400.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc4.0 \
    && tar xzf /tmp/msvc400.tar.gz -C /opt/msvc4.0 --strip-components=1 \
    && rm /tmp/msvc400.tar.gz \
    && ls /opt/msvc4.0/BIN/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc4.0/BIN/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'rebrew_run /opt/msvc4.0/BIN/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
