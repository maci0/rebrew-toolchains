# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcps2-3.0b22-020926

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0b22-020926 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0b22-020926 (CodeWarrior PS2, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/ps2_compilers.tar.xz" \
    && echo "f337a65a4fbab5cf0e335efe266dcbc7cf69b19c665c6b3a8924736df151a02a  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwcps2-3.0b22-020926 /tmp/x \
    && tar xJf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/mwcps2-3.0b22-020926/. /opt/mwcps2-3.0b22-020926/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwcps2-3.0b22-020926/mwccps2.exe

COPY mwcps2-wrapper.sh /usr/local/bin/mwcps2
RUN chmod +x /usr/local/bin/mwcps2

ENTRYPOINT ["/usr/local/bin/mwcps2"]

USER rebrew
