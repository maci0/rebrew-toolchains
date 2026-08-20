# MSVC 4.2 — 32-bit PE compiler under wine (archaic-msvc/msvc420 snapshot).
#
# Inherits the shared rebrew/base; this image adds the MSVC 4.2
# command-line toolchain (archaic-msvc/msvc420 repo tarball, sha256-pinned)
# and the `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:4.2-win32 toolchain/msvc/4.2-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:4.2-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.2 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.2 (win32, wine) toolchain image"

# MSVC 4.2 command-line toolchain — archaic-msvc/msvc420 repo tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the committed toolchain/msvc/4.2-win32).
RUN curl -sL -o /tmp/msvc420.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc420/tar.gz/refs/heads/master" \
    && echo "651db241202416be7e870ff8d98928179b94515068e7895008b8a82cb0b7001c  /tmp/msvc420.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc4.2 \
    && tar xzf /tmp/msvc420.tar.gz -C /opt/msvc4.2 --strip-components=1 \
    && rm /tmp/msvc420.tar.gz \
    && ls /opt/msvc4.2/bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc4.2/bin/CL.EXE <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc4.2/bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
