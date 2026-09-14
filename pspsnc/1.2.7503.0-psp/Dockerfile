# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: pspsnc-1.2.7503.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSPSNC 1.2.7503.0 (PSP)" \
      org.opencontainers.image.description="PSPSNC 1.2.7503.0 (Sony PSP, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/pspsnc_1.2.7503.0.tar.gz" \
    && echo "0d10a4b387e45b62369eea21b6693fc5517335033bf65e65aa7b543a916f4d6d  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/pspsnc-1.2.7503.0 \
    && tar xzf /tmp/compiler.tar.gz -C /opt/pspsnc-1.2.7503.0 \
    && rm /tmp/compiler.tar.gz \
    && ls /opt/pspsnc-1.2.7503.0/pspsnc.exe

COPY pspsnc-wrapper.sh /usr/local/bin/pspsnc
RUN chmod +x /usr/local/bin/pspsnc

ENTRYPOINT ["/usr/local/bin/pspsnc"]

USER rebrew
