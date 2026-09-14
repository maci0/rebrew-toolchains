# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mingw-16.2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MinGW-w64 GCC 16.2.0 (win32, wine)" \
      org.opencontainers.image.description="MinGW-w64 GCC 16.2.0 (i686-w64-mingw32, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends p7zip-full \
    && rm -rf /var/lib/apt/lists/*

ENV WINEPATH="Z:\\opt\\mingw-16.2.0\\bin"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mingw.7z \
        "https://github.com/niXman/mingw-builds-binaries/releases/download/16.2.0-rt_v14-rev1/i686-16.2.0-release-posix-dwarf-msvcrt-rt_v14-rev1.7z" \
    && echo "9773342cba88efe50e6f3ddd021ac6f1d9ac1957301705fe64def22f501f0dd4  /tmp/mingw.7z" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mingw-16.2.0 \
    && 7z x -y -o/tmp/mingw /tmp/mingw.7z >/dev/null \
    && cp -a /tmp/mingw/mingw32/. /opt/mingw-16.2.0/ \
    && rm -rf /tmp/mingw /tmp/mingw.7z \
    && ls /opt/mingw-16.2.0/bin/i686-w64-mingw32-gcc.exe

COPY mingw-wrapper.sh /usr/local/bin/mingw
RUN chmod +x /usr/local/bin/mingw

ENTRYPOINT ["/usr/local/bin/mingw"]

USER rebrew
