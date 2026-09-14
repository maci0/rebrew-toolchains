# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ghs-5.3.22

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Green Hills 5.3.22 (Wii U)" \
      org.opencontainers.image.description="Green Hills C/C++ 5.3.22 (Wii U PowerPC, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ghs.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ghs5.3.22.tar.gz" \
    && echo "41cd0a4723acfbddf8f70a9c3ff84bce7e85087b1d1ccef8bbf5f03d82c2b520  /tmp/ghs.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ghs-5.3.22 \
    && tar xzf /tmp/ghs.tar.gz -C /opt/ghs-5.3.22 \
    && rm /tmp/ghs.tar.gz \
    && ls /opt/ghs-5.3.22/bin/cxppc.exe

COPY cxppc-wrapper.sh /usr/local/bin/cxppc
RUN chmod +x /usr/local/bin/cxppc

ENTRYPOINT ["/usr/local/bin/cxppc"]

USER rebrew
