# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psp-gcc-1.3.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSP GCC 1.3.1" \
      org.opencontainers.image.description="PSP GCC 1.3.1 (mipsallegrex, PS1-family MIPS, 32-bit host) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psp.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psp-gcc-1.3.1.tar.gz" \
    && echo "788b6d2c0ed920da6b1e5a350d23dd7ea05820526e23f9b5b967b3b238ea2e2e  /tmp/psp.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/psp-gcc-1.3.1 /tmp/psp \
    && tar xzf /tmp/psp.tar.gz -C /tmp/psp \
    && cp -r /tmp/psp/. /opt/psp-gcc-1.3.1/ \
    && cp -r /tmp/psp/psp/bin /tmp/psp/psp/include /opt/psp-gcc-1.3.1/ \
    && cp -r /tmp/psp/psp/lib/. /opt/psp-gcc-1.3.1/lib/ \
    && rm -rf /tmp/psp /tmp/psp.tar.gz \
    && chmod -R a+rX /opt/psp-gcc-1.3.1 \
    && mkdir -p /usr/local/psp \
    && ln -s /opt/psp-gcc-1.3.1 /usr/local/psp/devkit \
    && find /opt/psp-gcc-1.3.1 -name cc1 | grep .

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
