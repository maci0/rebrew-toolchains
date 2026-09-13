# Watcom C/C++ 10.0a (DOS-era release) — 32-bit Watcom C compiler (wcc386, Windows PE).
#
# Inherits the shared rebrew/base; this image installs the pinned Watcom C/C++ 10.0a (DOS-era release)
# tree and exposes wcc386 as the entrypoint.  The Windows-host compiler runs
# through the shared wine/wibo dispatcher, like decomp.me's own image for
# this release (wibo is a supported override via REBREW_RUNNER).  The tree
# also carries wpp386.exe (the C++ driver) and the 16-bit DOS compilers.
#
# Build:  docker build -t rebrew/watcom:10.0a-win32 watcom/10.0a-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:10.0a-win32 -zq -fo=t.obj t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.0a (DOS-era release) (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.0a (DOS-era release) (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.0a \
    INCLUDE=/opt/watcom-10.0a/h

RUN mkdir -p /opt/watcom-10.0a /tmp/watcom \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/wcc10.0a.tar.gz" \
    && echo "920a9674d1b10f227ae65171c187212b06d7fc38b263313922615c4f5e9b24a6  /tmp/watcom/watcom.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.0a \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.0a/binnt/wcc386.exe

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
