# MSVC 7.1-sp1 — 32-bit PE compiler under wine (archaic-msvc/msvc710_sp1).
#
# Inherits the shared rebrew/base; this image adds the MSVC 7.1-sp1
# command-line toolchain (archaic-msvc/msvc710_sp1 tarball, sha256-pinned) and the
# `cl` entrypoint wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:7.1-sp1-win32 toolchain/msvc/7.1-sp1-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:7.1-sp1-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.1-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.1-sp1 (win32, wine) toolchain image"

# MSVC 7.1-sp1 command-line toolchain — archaic-msvc/msvc710_sp1 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from — byte-identical to the vendored toolchain/msvc/7.1-sp1-win32).
RUN curl -sL -o /tmp/msvc710_sp1.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc710_sp1/tar.gz/refs/heads/master" \
    && echo "44246ff2980d715c2d05eaed505344a0b87850a04606482c13ba4832ddf5ec70  /tmp/msvc710_sp1.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc7.1-sp1 \
    && tar xzf /tmp/msvc710_sp1.tar.gz -C /opt/msvc7.1-sp1 --strip-components=1 \
    && rm /tmp/msvc710_sp1.tar.gz \
    && ls /opt/msvc7.1-sp1/Vc7/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc7.1-sp1/Vc7/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc7.1-sp1/Vc7/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
