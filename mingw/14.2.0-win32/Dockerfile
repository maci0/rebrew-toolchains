# MinGW-w64 GCC 14.2.0 (i686 target) — 32-bit PE cross compiler under wine.
#
# Inherits the shared rebrew/base; this image downloads the pinned
# niXman/mingw-builds-binaries release asset and installs it to
# /opt/mingw-14.2.0.  The release assets are Windows-host binaries
# (PE32 i386: bin/i686-w64-mingw32-gcc.exe), so the entrypoint runs the
# driver through the shared wine/wibo dispatcher like the other PE
# toolchains — the target is 32-bit Windows (.obj / COFF).
#
# Build:  docker build -t rebrew/mingw:14.2.0-win32 mingw/14.2.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/mingw:14.2.0-win32 -c t.c -o t.o  (ENTRYPOINT is the MinGW wrapper)

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

# Install steps need root; the base image defaults to a non-root user.
USER root

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MinGW-w64 GCC 14.2.0 (win32, wine)" \
      org.opencontainers.image.description="MinGW-w64 GCC 14.2.0 (i686-w64-mingw32, PE/x86_32) toolchain image"

# The upstream asset is a .7z archive.
RUN apt-get update \
    && apt-get install -y --no-install-recommends p7zip-full \
    && rm -rf /var/lib/apt/lists/*

# MinGW-w64 GCC 14.2.0 release asset (sha256-verified).  The archive wraps
# everything in a single mingw32/ directory, which is stripped so the
# install root holds bin/ and the i686-w64-mingw32/ sysroot directly.
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mingw.7z \
        "https://github.com/niXman/mingw-builds-binaries/releases/download/14.2.0-rt_v12-rev2/i686-14.2.0-release-posix-dwarf-msvcrt-rt_v12-rev2.7z" \
    && echo "895d22c902e22d4b7b1c1b4160d1b3d70bbd6fc653b04f46b7736ef0ef5e4bc2  /tmp/mingw.7z" | sha256sum -c - \
    && mkdir -p /opt/mingw-14.2.0 \
    && 7z x -y -o/tmp/mingw /tmp/mingw.7z >/dev/null \
    && cp -a /tmp/mingw/mingw32/. /opt/mingw-14.2.0/ \
    && rm -rf /tmp/mingw /tmp/mingw.7z \
    && ls /opt/mingw-14.2.0/bin/i686-w64-mingw32-gcc.exe

# mingw-builds keeps the driver's runtime DLLs (libwinpthread-1.dll, ...) in
# bin/ while cc1.exe lives in libexec/gcc/...; wine resolves a spawned tool's
# imports through WINEPATH, so point it at bin/ — 14.2.0's cc1.exe otherwise
# fails with STATUS_DLL_NOT_FOUND (wine: c0000135) and the driver exits 1
# without producing an object.
ENV WINEPATH="Z:\\opt\\mingw-14.2.0\\bin"

# The MinGW wrapper: the compiler is a Windows PE binary, so it runs
# through the shared runner (wine by default, wibo when REBREW_RUNNER=wibo)
# under the common watchdog.  POSIX argv passes through unchanged.
RUN printf '%s\n' \
        '#!/bin/sh' \
        '. /usr/local/lib/rebrew/wrapper-common.sh' \
        'rebrew_run /opt/mingw-14.2.0/bin/i686-w64-mingw32-gcc.exe "$@"' \
        > /usr/local/bin/mingw \
    && chmod +x /usr/local/bin/mingw

ENTRYPOINT ["/usr/local/bin/mingw"]

# Runtime drops back to the base image's non-root user.
USER rebrew
