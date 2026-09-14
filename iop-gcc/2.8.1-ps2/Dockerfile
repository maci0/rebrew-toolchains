# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: iop-gcc-2.8.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IOP-GCC 2.8.1 (PS2)" \
      org.opencontainers.image.description="IOP-GCC 2.8.1 (PS2 IOP, mipsel-scei-elfl, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/iop-gcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/iop-gcc2.8.1.tar.gz" \
    && echo "1f602e146f5be218cb3c84cda615432035bcf4a4f1a5f249164163a456ac929a  /tmp/iop-gcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/iop-gcc-2.8.1 \
    && tar xzf /tmp/iop-gcc.tar.gz -C /opt/iop-gcc-2.8.1 \
    && rm /tmp/iop-gcc.tar.gz \
    && chmod +x /opt/iop-gcc-2.8.1/bin/iop-gcc \
    && /opt/iop-gcc-2.8.1/bin/iop-gcc --version

COPY iop-gcc-wrapper.sh /usr/local/bin/iop-gcc
RUN chmod +x /usr/local/bin/iop-gcc

ENTRYPOINT ["/usr/local/bin/iop-gcc"]

USER rebrew
