# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcps2-3.0.1b87-031208

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0.1b87-031208 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0.1b87-031208 (CodeWarrior PS2, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-3.0.1b87-031208.tar.gz" \
    && echo "3718581319518c9a3cece4ded2951a5e7828123c069c9bbc4d854e8b1c46b718  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwcps2-3.0.1b87-031208 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwcps2-3.0.1b87-031208/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwcps2-3.0.1b87-031208/mwccps2.exe

COPY mwcps2-wrapper.sh /usr/local/bin/mwcps2
RUN chmod +x /usr/local/bin/mwcps2

ENTRYPOINT ["/usr/local/bin/mwcps2"]

USER rebrew
