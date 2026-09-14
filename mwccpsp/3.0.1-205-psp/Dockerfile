# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccpsp-3.0.1-205

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-205 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1-205 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_205.tar.gz" \
    && echo "ace61d4641fcdff55c08b7560c95915b20243f0f18023c3d4ce99fe37c5cdb00  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwccpsp-3.0.1-205 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwccpsp-3.0.1-205/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwccpsp-3.0.1-205/mwccpsp.exe

COPY mwccpsp-wrapper.sh /usr/local/bin/mwccpsp
RUN chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
