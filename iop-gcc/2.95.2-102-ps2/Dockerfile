# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: iop-gcc-2.95.2-102

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IOP-GCC 2.95.2-102 (PS2)" \
      org.opencontainers.image.description="IOP-GCC 2.95.2 build 102 (PS2 IOP, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/iop-gcc2.95.2-102.tar.gz" \
    && echo "84016c5899358f65bb320081087f7fb82e32fd5f4ab25733bec094d4baa9728a  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/iop-gcc-2.95.2-102 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/iop-gcc-2.95.2-102 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/iop-gcc-2.95.2-102/bin/iop-gcc.exe

COPY iop-gcc-wrapper.sh /usr/local/bin/iop-gcc
RUN chmod +x /usr/local/bin/iop-gcc

ENTRYPOINT ["/usr/local/bin/iop-gcc"]

USER rebrew
