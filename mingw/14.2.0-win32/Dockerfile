# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mingw-14.2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MinGW-w64 GCC 14.2.0 (win32, wine)" \
      org.opencontainers.image.description="MinGW-w64 GCC 14.2.0 (i686-w64-mingw32, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends p7zip-full \
    && rm -rf /var/lib/apt/lists/*

ENV WINEPATH="Z:\\opt\\mingw-14.2.0\\bin"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mingw.7z \
        "https://github.com/niXman/mingw-builds-binaries/releases/download/14.2.0-rt_v12-rev2/i686-14.2.0-release-posix-dwarf-msvcrt-rt_v12-rev2.7z" \
    && echo "895d22c902e22d4b7b1c1b4160d1b3d70bbd6fc653b04f46b7736ef0ef5e4bc2  /tmp/mingw.7z" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mingw-14.2.0 \
    && 7z x -y -o/tmp/mingw /tmp/mingw.7z >/dev/null \
    && cp -a /tmp/mingw/mingw32/. /opt/mingw-14.2.0/ \
    && rm -rf /tmp/mingw /tmp/mingw.7z \
    && ls /opt/mingw-14.2.0/bin/i686-w64-mingw32-gcc.exe

COPY mingw-wrapper.sh /usr/local/bin/mingw
RUN chmod +x /usr/local/bin/mingw

ENTRYPOINT ["/usr/local/bin/mingw"]

USER rebrew
