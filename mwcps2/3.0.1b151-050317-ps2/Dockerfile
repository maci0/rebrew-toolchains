# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcps2-3.0.1b151-050317

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 3.0.1b151-050317 (PS2)" \
      org.opencontainers.image.description="MWCPS2 3.0.1b151-050317 (CodeWarrior PS2, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-3.0.1b151-050317.tar.gz" \
    && echo "5050a211954f0828cf1c0f56333943407d20f7e85bc68b23e3c539bb5d8ee947  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwcps2-3.0.1b151-050317 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwcps2-3.0.1b151-050317/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwcps2-3.0.1b151-050317/mwccps2.exe

COPY mwcps2-wrapper.sh /usr/local/bin/mwcps2
RUN chmod +x /usr/local/bin/mwcps2

ENTRYPOINT ["/usr/local/bin/mwcps2"]

USER rebrew
