# MSVC 7.0-rtm — 32-bit PE compiler under wine (archaic-msvc/msvc700).
#
# Inherits the shared rebrew/base; this image adds the MSVC 7.0-rtm
# command-line toolchain (archaic-msvc/msvc700 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:7.0-rtm-win32 toolchain/msvc/7.0-rtm-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:7.0-rtm-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.0-rtm (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.0-rtm (win32, wine) toolchain image"

# MSVC 7.0-rtm command-line toolchain — archaic-msvc/msvc700 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/7.0-rtm-win32).
RUN curl -sL -o /tmp/msvc700.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc700/tar.gz/refs/heads/master" \
    && echo "5f75462fb6134ad56c3ae28cf8b1e3b2869578d4171568b7a1fcdfb0bf97830b  /tmp/msvc700.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc7.0-rtm \
    && tar xzf /tmp/msvc700.tar.gz -C /opt/msvc7.0-rtm --strip-components=1 \
    && rm /tmp/msvc700.tar.gz \
    && ls /opt/msvc7.0-rtm/Vc7/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc7.0-rtm/Vc7/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc7.0-rtm/Vc7/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
