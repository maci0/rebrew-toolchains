# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-10.6-cxx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Watcom C/C++ 10.6 (win32)" \
      org.opencontainers.image.description="Watcom C/C++ 10.6 (wcc386, PE/x86_32, wine/wibo) toolchain image"

ENV WATCOM=/opt/watcom-10.6-cxx \
    INCLUDE=/opt/watcom-10.6-cxx/h

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/watcom/watcom.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/wcc10.5/wcc10.6.tar.gz" \
    && echo "c455edf32dc73f29c2b4e0aa5c6988768809641033ef54700725242711b04e29  /tmp/watcom/watcom.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/watcom-10.6-cxx /tmp/watcom \
    && tar xzf /tmp/watcom/watcom.tar.gz -C /opt/watcom-10.6-cxx \
    && rm -rf /tmp/watcom \
    && ls /opt/watcom-10.6-cxx/binnt/wpp386.exe \
    && chmod +x /usr/local/bin/wpp386

COPY wpp386-wrapper.sh /usr/local/bin/wpp386
RUN chmod +x /usr/local/bin/wpp386

ENTRYPOINT ["/usr/local/bin/wpp386"]

USER rebrew
