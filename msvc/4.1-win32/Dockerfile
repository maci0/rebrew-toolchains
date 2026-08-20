# MSVC 4.1 — 32-bit PE compiler under wine (archaic-msvc/msvc410).
#
# Inherits the shared rebrew/base; this image adds the MSVC 4.1
# command-line toolchain (archaic-msvc/msvc410 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:4.1-win32 toolchain/msvc/4.1-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:4.1-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.1 (win32, wine) toolchain image"

# MSVC 4.1 command-line toolchain — archaic-msvc/msvc410 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/4.1-win32).
RUN curl -sL -o /tmp/msvc410.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc410/tar.gz/refs/heads/master" \
    && echo "21486aecd108397bdced6e2cf6a5170a3cc30280a3eba97a4a8f92985a9cc5c4  /tmp/msvc410.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc4.1 \
    && tar xzf /tmp/msvc410.tar.gz -C /opt/msvc4.1 --strip-components=1 \
    && rm /tmp/msvc410.tar.gz \
    && ls /opt/msvc4.1/bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc4.1/bin/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc4.1/bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
