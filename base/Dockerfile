# rebrew/base — the shared OS + wine layer for every toolchain image.
#
# All toolchain Dockerfiles inherit FROM this image, so the OS, wine,
# dosbox and download tooling are built once and cached; each toolchain
# image only adds its compiler + an entrypoint wrapper.
#
# Build:  docker build -t rebrew/base:1.0 toolchain/base
# Invoke: (base has no entrypoint — toolchain images set their own)
#
# Contents:
#   - wine + wine32 (32-bit PE compilers under wine, e.g. MSVC 6.0)
#   - dosbox (16-bit DOS compilers, e.g. MSVC 1.52, Delphi 1.0)
#   - dumb-init (signal handling for the compile containers)
#   - curl / ca-certificates / xz-utils (tarball-based toolchains)
#   - p7zip + unrar (extract the Borland InstallShield / MSVC 1.52 RAR SFX
#     archives the toolchain Dockerfiles download)
#   - /usr/local/lib/rebrew/wrapper-common.sh (shared wrapper helpers)
#   - common env: WINEDEBUG=-all, WINEPREFIX=/opt/wineprefix,
#     SDL_VIDEODRIVER=dummy (headless)
#
# Determinism: the debian base is pinned to a digest so apt resolves the
# same snapshot on every build.  Toolchain downloads are pinned by sha256
# in the per-toolchain Dockerfiles.

# debian:bookworm-slim@sha256:362e64223cc0da95422b3b13c045186fc0a81250e765d31c025fbddf257f6143
FROM debian:bookworm-slim@sha256:362e64223cc0da95422b3b13c045186fc0a81250e765d31c025fbddf257f6143

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base (OS + wine + dosbox + wrapper helpers)" \
      org.opencontainers.image.description="base (OS + wine + dosbox + wrapper helpers) toolchain image"

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        wine wine32 dosbox dumb-init curl ca-certificates xz-utils \
        p7zip-full \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDEBUG=-all \
    WINEPREFIX=/opt/wineprefix \
    SDL_VIDEODRIVER=dummy

COPY wrapper-common.sh /usr/local/lib/rebrew/wrapper-common.sh
RUN chmod +x /usr/local/lib/rebrew/wrapper-common.sh
