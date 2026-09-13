# Watcom C/C++ 11.0 — 32-bit Watcom C compiler (wcc386, Windows PE).
#
# Inherits the shared rebrew/base; this image installs the pinned Watcom C/C++ 11.0
# tree and exposes wcc386 as the entrypoint.  The Windows-host compiler runs
# through the shared wine/wibo dispatcher, like decomp.me's own image for
# this release (wibo is a supported override via REBREW_RUNNER).  The tree
# also carries wpp386.exe (the C++ driver) and the 16-bit DOS compilers.
#
# Build:  docker build -t rebrew/watcom:11.0-win32 watcom/11.0-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:11.0-win32 -zq -fo=t.obj t.c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 11.0 (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 11.0 (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-11.0 \
    INCLUDE=/opt/watcom-11.0/h

RUN mkdir -p /opt/watcom-11.0 /tmp/watcom \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc11.0.tar.gz" \
    && echo "6ecbf03ad4d71285f5813c34a4f551720eec0dfb09996a7dda7cb591963df325  /tmp/watcom/watcom.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-11.0 \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-11.0/binnt/wcc386.exe

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
