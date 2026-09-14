# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccpsp-3.0.1-180

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-180 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1-180 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_180.tar.gz" \
    && echo "2d4ff76e4e5c9bd938dbc627e4219583d6119bc4af30548df43e06221ab7b32b  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwccpsp-3.0.1-180 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwccpsp-3.0.1-180/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwccpsp-3.0.1-180/mwccpsp.exe

COPY mwccpsp-wrapper.sh /usr/local/bin/mwccpsp
RUN chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
