# MSVC 5.0-sp3 — 32-bit PE compiler under wine (archaic-msvc/msvc500sp3).
#
# Inherits the shared rebrew/base; this image adds the MSVC 5.0-sp3
# command-line toolchain (archaic-msvc/msvc500sp3 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:5.0-sp3-win32 toolchain/msvc/5.0-sp3-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:5.0-sp3-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0-sp3 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0-sp3 (win32, wine) toolchain image"

# MSVC 5.0-sp3 command-line toolchain — archaic-msvc/msvc500sp3 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/5.0-sp3-win32).
RUN curl -sL -o /tmp/msvc500sp3.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500sp3/tar.gz/refs/heads/master" \
    && echo "cdba2878eaacd07cb289b73f08250e2c39596fc9b31a2ad7a4fd887879be1e38  /tmp/msvc500sp3.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc5.0-sp3 \
    && tar xzf /tmp/msvc500sp3.tar.gz -C /opt/msvc5.0-sp3 --strip-components=1 \
    && rm /tmp/msvc500sp3.tar.gz \
    && ls /opt/msvc5.0-sp3/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc5.0-sp3/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc5.0-sp3/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
