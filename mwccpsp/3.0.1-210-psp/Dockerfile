# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccpsp-3.0.1-210

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-210 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1 build 210 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwccpsp.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_210.tar.gz" \
    && echo "a8a0bf3a0ec3545f6578717516aad0f262a40dd1538a6e462b77efc29e79a969  /tmp/mwccpsp.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwccpsp-3.0.1-210 \
    && tar xzf /tmp/mwccpsp.tar.gz -C /opt/mwccpsp-3.0.1-210 \
    && rm /tmp/mwccpsp.tar.gz \
    && ls /opt/mwccpsp-3.0.1-210/mwccpsp.exe

COPY mwccpsp-wrapper.sh /usr/local/bin/mwccpsp
RUN chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
