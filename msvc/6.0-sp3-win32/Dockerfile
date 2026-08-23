# MSVC 6.0-sp3 — 32-bit PE compiler under wine (archaic-toolchains/msvc600_sp3).
#
# Inherits the shared rebrew/base; this image adds the MSVC 6.0-sp3
# command-line toolchain (archaic-toolchains/msvc600_sp3 repo tarball, sha256-pinned)
# and the `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:6.0-sp3-win32 msvc/6.0-sp3-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-sp3-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp3 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp3 (win32, wine) toolchain image"

# MSVC 6.0-sp3 command-line toolchain — archaic-toolchains/msvc600_sp3 repo
# tarball (sha256-verified; CL.EXE byte-identical to the OmniBlade decomp.me
# msvc6.3 this image previously built from — only the VC98/Bin layout differs
# from the older flat Bin/ tree).
RUN curl -fsSL -o /tmp/msvc6.0-sp3.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc600_sp3/tar.gz/refs/heads/main" \
    && echo "f753adfa8a29d8b03fb67bbcaadd3e41d672b86e5e17e32084bd1b60a1771ab4  /tmp/msvc6.0-sp3.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc6.0-sp3 \
    && tar xzf /tmp/msvc6.0-sp3.tar.gz -C /opt/msvc6.0-sp3 --strip-components=1 \
    && rm /tmp/msvc6.0-sp3.tar.gz \
    && ls /opt/msvc6.0-sp3/VC98/Bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc6.0-sp3/VC98/Bin/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'rebrew_run /opt/msvc6.0-sp3/VC98/Bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
