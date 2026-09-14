# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-10.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.5 (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.5 (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.5 \
    INCLUDE=/opt/watcom-10.5/h

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc10.5.tar.gz" \
    && echo "70acc3b4b4729e44c149b53553a3c35aa4070ed34d6790b034273506d5c5b3fb  /tmp/watcom/watcom.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/watcom-10.5 /tmp/watcom \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.5 \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.5/binnt/wcc386.exe \
    && chmod +x /usr/local/bin/wcc386

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
