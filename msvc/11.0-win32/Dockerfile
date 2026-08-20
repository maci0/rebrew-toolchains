# MSVC 11.0 — 32-bit PE compiler under wine (archaic-msvc/msvc1100).
#
# Inherits the shared rebrew/base; this image adds the MSVC 11.0 (VS 2012)
# command-line toolchain (archaic-msvc/msvc1100 tarball, sha256-pinned —
# cl.exe 17.00.50522.1) and the `cl` entrypoint wrapper.  Fully
# self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:11.0-win32 toolchain/msvc/11.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:11.0-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 11.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 11.0 (win32, wine) toolchain image"

# MSVC 11.0 command-line toolchain — archaic-msvc/msvc1100 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from).
RUN curl -sL -o /tmp/msvc1100.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc1100/tar.gz/refs/heads/master" \
    && echo "adba1882eb076cb774b7a5d0f2b1067544da7cd2f0bf0b12f284361516cbc825  /tmp/msvc1100.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc11.0 \
    && tar xzf /tmp/msvc1100.tar.gz -C /opt/msvc11.0 --strip-components=1 \
    && rm /tmp/msvc1100.tar.gz \
    && ls /opt/msvc11.0/VC/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc11.0/VC/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc11.0/VC/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
