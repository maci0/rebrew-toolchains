# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-10.0a

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.0a (DOS-era release) (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.0a (DOS-era release) (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.0a \
    INCLUDE=/opt/watcom-10.0a/h

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/wcc10.0a.tar.gz" \
    && echo "920a9674d1b10f227ae65171c187212b06d7fc38b263313922615c4f5e9b24a6  /tmp/watcom/watcom.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/watcom-10.0a /tmp/watcom \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.0a \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.0a/binnt/wcc386.exe

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
