# MSVC 8.0 (portable repack) — decomp.me's `msvc8.0p`.
#
# Inherits the shared rebrew/base; this image installs the pinned
# widberg/msvc8.0 *portable* repack (commit 52c8293f) and exposes cl.exe
# under the shared wine/wibo dispatcher.  The tree is flat (bin/, include/,
# lib/) rather than a Visual Studio layout, so the wrapper points INCLUDE and
# LIB at those directories.
#
# It reports the same version as `msvc/8.0-win32` (14.00.50727.42) but its
# binaries differ (`cl.exe` `6e7de73a82ac` vs `3cbf4306526c`): the portable
# repack patches VC8 to run outside a full VS install, which is why decomp.me
# lists it as its own id.  The other widberg commit (d6c4aa20, id `msvc8.0`)
# is byte-identical to this repo's own tree and is not shipped separately.
#
# Build:  docker build -t rebrew/msvc:8.0-portable-win32 msvc/8.0-portable-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:8.0-portable-win32 /c f.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 8.0 portable repack (win32)" \
      org.opencontainers.image.description="MSVC 8.0 (portable preservation repack, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/msvc8.0-portable /tmp/msvc8p \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc8p/msvc.zip \
        "https://github.com/widberg/msvc8.0/archive/52c8293f8b8d6441c594cf096542290c17a4d70e.zip" \
    && echo "b138c1b3c99a8a2b9c4324add058e0ddfda5def81f0ef821b10cbfcf383b2084  /tmp/msvc8p/msvc.zip" | sha256sum -c - \
    && unzip -q /tmp/msvc8p/msvc.zip -d /tmp/msvc8p/x \
    && cp -a /tmp/msvc8p/x/msvc8.0-52c8293f8b8d6441c594cf096542290c17a4d70e/. /opt/msvc8.0-portable/ \
    && rm -rf /tmp/msvc8p \
    && ls /opt/msvc8.0-portable/bin/cl.exe

RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'export INCLUDE="Z:\\opt\\msvc8.0-portable\\include"' \
        'export LIB="Z:\\opt\\msvc8.0-portable\\lib"' \
        'rebrew_run /opt/msvc8.0-portable/bin/cl.exe "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
