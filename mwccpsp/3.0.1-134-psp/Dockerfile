# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwccpsp-3.0.1-134

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCCPSP 3.0.1-134 (PSP)" \
      org.opencontainers.image.description="MWCCPSP 3.0.1-134 (CodeWarrior PSP, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compiler.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwccpsp_3.0.1_134.tar.gz" \
    && echo "a4a00c2450ee2b6f7be29fc73470446994fcf2b1b1003b8ac34568f3358e1c99  /tmp/compiler.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwccpsp-3.0.1-134 /tmp/x \
    && tar xzf /tmp/compiler.tar.gz -C /tmp/x \
    && cp -a /tmp/x/. /opt/mwccpsp-3.0.1-134/ \
    && rm -rf /tmp/x /tmp/compiler.tar.gz \
    && ls /opt/mwccpsp-3.0.1-134/mwccpsp.exe

COPY mwccpsp-wrapper.sh /usr/local/bin/mwccpsp
RUN chmod +x /usr/local/bin/mwccpsp

ENTRYPOINT ["/usr/local/bin/mwccpsp"]

USER rebrew
