# Watcom C/C++ 10.5a — 32-bit Watcom C compiler (wcc386, Windows PE).
#
# Inherits the shared rebrew/base; this image installs the pinned Watcom C/C++ 10.5a
# tree and exposes wpp386 as the entrypoint.  The Windows-host compiler runs
# through the shared wine/wibo dispatcher, like decomp.me's own image for
# this release (wibo is a supported override via REBREW_RUNNER).  The same tree
# carries wcc386.exe for C; decomp.me's `wpp<version>` ids use the C++ driver,
# so this image is a C++ sibling rather than an alias of the C one.
#
# Build:  docker build -t rebrew/watcom:10.5a-cxx-win32 watcom/10.5a-cxx-win32
# Invoke: docker run --rm -v "$PWD":/work -w /work rebrew/watcom:10.5a-cxx-win32 -zq -fo=t.obj t.cpp

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.5a (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.5a (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.5a-cxx \
    INCLUDE=/opt/watcom-10.5a-cxx/h

RUN mkdir -p /opt/watcom-10.5a-cxx /tmp/watcom \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc10.5a.tar.gz" \
    && echo "fd82fd36594f1f1333d2b8a4b87956c1dfaacd2c9b3535db556bcf482f81adab  /tmp/watcom/watcom.tar.gz" | sha256sum -c - \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.5a-cxx \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.5a-cxx/binnt/wpp386.exe

COPY wpp386-wrapper.sh /usr/local/bin/wpp386
RUN chmod +x /usr/local/bin/wpp386

ENTRYPOINT ["/usr/local/bin/wpp386"]

USER rebrew
