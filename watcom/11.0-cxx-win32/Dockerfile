# Watcom C/C++ 11.0 — 32-bit Watcom C compiler (wcc386, Windows PE).
#
# Inherits the shared rebrew/base; this image installs the pinned Watcom C/C++ 11.0
# tree and exposes wpp386 as the entrypoint.  The Windows-host compiler runs
# through the shared wine/wibo dispatcher, like decomp.me's own image for
# this release (wibo is a supported override via REBREW_RUNNER).  The same tree
# carries wcc386.exe for C; decomp.me's `wpp<version>` ids use the C++ driver,
# so this image is a C++ sibling rather than an alias of the C one.
#
# Build:  docker build -t rebrew/watcom:11.0-cxx-win32 watcom/11.0-cxx-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:11.0-cxx-win32 -zq -fo=t.obj t.cpp

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 11.0 (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 11.0 (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-11.0-cxx \
    INCLUDE=/opt/watcom-11.0-cxx/h

RUN mkdir -p /opt/watcom-11.0-cxx /tmp/watcom \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc11.0.tar.gz" \
    && echo "6ecbf03ad4d71285f5813c34a4f551720eec0dfb09996a7dda7cb591963df325  /tmp/watcom/watcom.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-11.0-cxx \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-11.0-cxx/binnt/wpp386.exe

COPY wpp386-wrapper.sh /usr/local/bin/wpp386
RUN chmod +x /usr/local/bin/wpp386

ENTRYPOINT ["/usr/local/bin/wpp386"]

USER rebrew
