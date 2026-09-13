# MSVC 6.0 (Windows 9x repack) — a distinct preserved build of VC6.
#
# Inherits the shared rebrew/base; this image installs the pinned OmniBlade
# `msvcwin9x` repack, i.e. the tree decomp.me serves under its `msvc6.0`
# id.  It is *not* the same build as this repo's `msvc/6.0-win32` image:
# both report compiler banner 12.00.8168, but their front ends differ
# (`c1xx.dll` here `71554a7688` vs `f3f0245453` there), so both are
# shipped and the community id maps here.  See docs/PROVENANCE.md.
#
# The repack carries headers and binaries but no library set, so it compiles
# objects (/c) but cannot link — the same way decomp.me uses it.
#
# Build:  docker build -t rebrew/msvc:6.0-win9x-win32 msvc/6.0-win9x-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/msvc:6.0-win9x-win32 /c f.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 win9x repack (win32)" \
      org.opencontainers.image.description="MSVC 6.0 (Windows 9x preservation repack, PE/x86_32) toolchain image"

# OmniBlade's win9x repack (sha256-verified).  The tarball is flat: Bin/,
# Include/, ATL/, MFC/ at the root.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/msvc6.0-win9x \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc6.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/msvcwin9x/msvc6.0.tar.gz" \
    && echo "5c81e9c2ab0ac5545022c1418a23392cb514db950cf6dcb1f48327270403fcd3  /tmp/msvc6.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/msvc6.tar.gz -C /opt/msvc6.0-win9x \
    && rm /tmp/msvc6.tar.gz \
    && ls /opt/msvc6.0-win9x/Bin/CL.EXE

# The `cl` wrapper: validate the source (common helper), then run the PE
# driver through the shared wine/wibo dispatcher with the include path baked
# in as a Windows-style Z: path (wine maps the container root to Z:).
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_pick_source "$@"' \
        'export INCLUDE="Z:\\opt\\msvc6.0-win9x\\Include"' \
        'rebrew_run /opt/msvc6.0-win9x/Bin/CL.EXE "$@"' \
        > /usr/local/bin/cl \
    && chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

# Runtime drops back to the base image's non-root user.
USER rebrew
