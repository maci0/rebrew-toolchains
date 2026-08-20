# MSVC 5.0-sp2 — 32-bit PE compiler under wine (archaic-msvc/msvc500sp2).
#
# Inherits the shared rebrew/base; this image adds the MSVC 5.0-sp2
# command-line toolchain (archaic-msvc/msvc500sp2 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:5.0-sp2-win32 toolchain/msvc/5.0-sp2-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:5.0-sp2-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0-sp2 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0-sp2 (win32, wine) toolchain image"

# MSVC 5.0-sp2 command-line toolchain — archaic-msvc/msvc500sp2 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/5.0-sp2-win32).
RUN curl -sL -o /tmp/msvc500sp2.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500sp2/tar.gz/refs/heads/master" \
    && echo "551137506a6a98ca890bfe20df7d5833bc475cf7e2279d959eccce0485525c8e  /tmp/msvc500sp2.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc5.0-sp2 \
    && tar xzf /tmp/msvc500sp2.tar.gz -C /opt/msvc5.0-sp2 --strip-components=1 \
    && rm /tmp/msvc500sp2.tar.gz \
    && ls /opt/msvc5.0-sp2/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc5.0-sp2/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc5.0-sp2/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
