# MSVC 2.0 — 32-bit PE compiler under wine (archaic-msvc/msvc200).
#
# Inherits the shared rebrew/base; this image adds the MSVC 2.0
# command-line toolchain (archaic-msvc/msvc200 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:2.0-win32 toolchain/msvc/2.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:2.0-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 2.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 2.0 (win32, wine) toolchain image"

# MSVC 2.0 command-line toolchain — archaic-msvc/msvc200 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/2.0-win32).
RUN curl -sL -o /tmp/msvc200.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc200/tar.gz/refs/heads/master" \
    && echo "0b058f103fe6b615987a85d518d7fd23389fab67c9df3cadfae22f5a70d5d000  /tmp/msvc200.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc2.0 \
    && tar xzf /tmp/msvc200.tar.gz -C /opt/msvc2.0 --strip-components=1 \
    && rm /tmp/msvc200.tar.gz \
    && ls /opt/msvc2.0/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc2.0/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc2.0/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
