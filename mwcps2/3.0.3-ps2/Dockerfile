# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcps2-3.0.3

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0.3 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0.3 (CodeWarrior PS2, PE/x86_32) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwcps2.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-3.0.3-020716.tar.gz" \
    && echo "63f89baae691403294724178efbcfc9e1b9ac48151536b6a321b17eb8f9970e5  /tmp/mwcps2.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwcps2-3.0.3 \
    && tar xzf /tmp/mwcps2.tar.gz -C /opt/mwcps2-3.0.3 \
    && rm /tmp/mwcps2.tar.gz \
    && ls /opt/mwcps2-3.0.3/mwccps2.exe

COPY mwccps2-wrapper.sh /usr/local/bin/mwccps2
RUN chmod +x /usr/local/bin/mwccps2

ENTRYPOINT ["/usr/local/bin/mwccps2"]

USER rebrew
