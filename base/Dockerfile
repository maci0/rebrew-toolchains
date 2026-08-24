# rebrew/base — the shared OS + wine layer for every toolchain image.
#
# All toolchain Dockerfiles inherit FROM this image, so the OS, wine,
# dosbox and download tooling are built once and cached; each toolchain
# image only adds its compiler + an entrypoint wrapper.
#
# Build:  docker build -t rebrew/base:1.0 base
# Invoke: (base has no entrypoint — toolchain images set their own)
#
# Contents:
#   - wine + wine32 (32-bit PE compilers under wine, e.g. MSVC 6.0)
#   - wibo (minimal decompals PE loader — selectable per run via
#     REBREW_RUNNER=wibo for much faster compiles of plain console tools)
#   - dosbox (16-bit DOS compilers, e.g. MSVC 1.52, Delphi 1.0)
#   - dumb-init (PID-1 signal relay; no image entrypoint wraps with it —
#     available to callers who prepend it via --entrypoint)
#   - curl / ca-certificates / xz-utils (the pinned tarball downloads)
#   - /usr/local/lib/rebrew/wrapper-common.sh (shared wrapper helpers)
#   - common env: WINEDEBUG=-all, WINEPREFIX=/opt/wineprefix,
#     SDL_VIDEODRIVER=dummy (headless)
#   - REBREW_RUNNER (wine|wibo) selects the 32-bit PE runtime per run; the
#     wrapper-common rebrew_run helper dispatches on it
#
# Determinism: the debian base is pinned to a digest so apt resolves the
# same snapshot on every build.  Toolchain downloads are pinned by sha256
# in the per-toolchain Dockerfiles.

# debian:bookworm-slim@sha256:362e64223cc0da95422b3b13c045186fc0a81250e765d31c025fbddf257f6143
FROM debian:bookworm-slim@sha256:362e64223cc0da95422b3b13c045186fc0a81250e765d31c025fbddf257f6143

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base (OS + wine/wibo + dosbox + wrapper helpers)" \
      org.opencontainers.image.description="base (OS + wine/wibo + dosbox + wrapper helpers) toolchain image"

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        wine wine32 dosbox dumb-init curl ca-certificates xz-utils \
    && rm -rf /var/lib/apt/lists/*

# wibo — the minimal decompals PE loader (github.com/decompals/wibo), static
# x86_64 build, sha256-pinned from the 1.2.0 release.  Runs 32-bit PE
# command-line tools (cl.exe, bcc32.exe, ...) without a wine prefix; wrappers
# use it when REBREW_RUNNER=wibo (they default to wine).
RUN curl -fsSL --retry 3 --retry-all-errors -o /usr/local/bin/wibo \
        "https://github.com/decompals/wibo/releases/download/1.2.0/wibo-x86_64" \
    && echo "13f86a2d618f0dbe67179d349625345eabf9b46450295cb4c904e49f6aff85af  /usr/local/bin/wibo" | sha256sum -c - \
    && chmod +x /usr/local/bin/wibo \
    && wibo --version >/dev/null

ENV WINEDEBUG=-all \
    WINEPREFIX=/opt/wineprefix \
    SDL_VIDEODRIVER=dummy

COPY wrapper-common.sh /usr/local/lib/rebrew/wrapper-common.sh
RUN chmod +x /usr/local/lib/rebrew/wrapper-common.sh
