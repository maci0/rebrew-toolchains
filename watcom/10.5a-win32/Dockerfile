# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-10.5a

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.5a (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.5a (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.5a \
    INCLUDE=/opt/watcom-10.5a/h

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc10.5a.tar.gz" \
    && echo "fd82fd36594f1f1333d2b8a4b87956c1dfaacd2c9b3535db556bcf482f81adab  /tmp/watcom/watcom.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/watcom-10.5a /tmp/watcom \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.5a \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.5a/binnt/wcc386.exe

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
