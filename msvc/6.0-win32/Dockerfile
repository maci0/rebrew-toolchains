# MSVC 6.0 — 32-bit PE compiler under wine (archaic-msvc/msvc600).
#
# Inherits the shared rebrew/base; this image adds the MSVC 6.0
# command-line toolchain (archaic-msvc/msvc600 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:6.0-win32 toolchain/msvc/6.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0 (win32, wine) toolchain image"

# MSVC 6.0 command-line toolchain — archaic-msvc/msvc600 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/6.0-win32).
RUN curl -sL -o /tmp/msvc600.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600/tar.gz/refs/heads/master" \
    && echo "19b72020c8225f91d7345b16aa0acf1b31a4608ae1299693021491e7338d0ee8  /tmp/msvc600.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc6.0 \
    && tar xzf /tmp/msvc600.tar.gz -C /opt/msvc6.0 --strip-components=1 \
    && rm /tmp/msvc600.tar.gz \
    && ls /opt/msvc6.0/VC98/Bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc6.0/VC98/Bin/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc6.0/VC98/Bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
