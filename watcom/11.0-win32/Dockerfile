# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-11.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 11.0 (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 11.0 (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-11.0 \
    INCLUDE=/opt/watcom-11.0/h

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc11.0.tar.gz" \
    && echo "6ecbf03ad4d71285f5813c34a4f551720eec0dfb09996a7dda7cb591963df325  /tmp/watcom/watcom.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/watcom-11.0 /tmp/watcom \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-11.0 \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-11.0/binnt/wcc386.exe \
    && chmod +x /usr/local/bin/wcc386

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
