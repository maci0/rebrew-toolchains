# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-3.2-rh8

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew GCC 3.2 (Red Hat 8, i386 Linux)" \
      org.opencontainers.image.description="Red Hat 8 GCC 3.2 (i386-redhat-linux, native) toolchain image"

RUN mkdir -p /opt/rh8 /tmp/rh8 && curl -fsSL --retry 3 --retry-all-errors -o /tmp/rh8/rh8.tar.gz \
        "https://github.com/OmniBlade/decomp.me/releases/download/rh8_gcc3.2/rh8_gcc3.2.tar.gz" \
    && echo "4b6e6bb7b360dc62b3b2a3176563357ae651873e2b3e3523871b9c7d30417c7a  /tmp/rh8/rh8.tar.gz" | sha256sum -c -

RUN tar xzf /tmp/rh8/rh8.tar.gz -C /opt/rh8 \
    && rm -rf /tmp/rh8 \
    && ls /opt/rh8/bin/i386-redhat-linux-gcc

COPY gcc-wrapper.sh /usr/local/bin/gcc
RUN chmod +x /usr/local/bin/gcc

ENTRYPOINT ["/usr/local/bin/gcc"]

USER rebrew
