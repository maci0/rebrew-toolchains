# MSVC 9.0-sp1 — 32-bit PE compiler under wine (archaic-toolchains/msvc900_sp1).
#
# Inherits the shared rebrew/base; this image adds the MSVC 9.0-SP1
# command-line toolchain (archaic-toolchains/msvc900_sp1 tarball,
# sha256-pinned — the 15.00.30729 SP1 compiler) and the `cl` entrypoint
# wrapper.  Fully self-contained: no host files.
#
# Build:  docker build -t rebrew/msvc:9.0-sp1-win32 toolchain/msvc/9.0-sp1-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:9.0-sp1-win32 /c f.c  (ENTRYPOINT is the cl wrapper)

FROM rebrew/base:1.0

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 9.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 9.0-sp1 (win32, wine) toolchain image"

# MSVC 9.0-SP1 command-line toolchain — archaic-toolchains/msvc900_sp1 tarball
# (sha256-verified; same source the `rebrew toolchain vendor` host tree
# assembles from).
RUN curl -sL -o /tmp/msvc900_sp1.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc900_sp1/tar.gz/refs/heads/main" \
    && echo "33a66c779da39ab40518f24b75656f1f93cb1837a3d65a9b79188f41c2f2bd97  /tmp/msvc900_sp1.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/msvc9.0-sp1 \
    && tar xzf /tmp/msvc900_sp1.tar.gz -C /opt/msvc9.0-sp1 --strip-components=1 \
    && rm /tmp/msvc900_sp1.tar.gz \
    && ls /opt/msvc9.0-sp1/VC/bin/cl.exe

# The `cl` wrapper: validate the source (common helper), then translate the
# MSVC-style argv into `wine /opt/msvc9.0-sp1/VC/bin/cl.exe <args>` inside the
# mounted /work.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'exec wine /opt/msvc9.0-sp1/VC/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]
