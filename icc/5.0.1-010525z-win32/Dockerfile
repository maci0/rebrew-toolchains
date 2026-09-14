# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: icc-5.0.1-010525z

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Intel C++ 5.0.1 (win32)" \
      org.opencontainers.image.description="Intel C++ Compiler 5.0.1 build 010525Z (i386 COFF, wine/wibo) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/icc.tar.gz \
        "https://github.com/bwrsandman/icc5.0.1.010525Z/releases/download/v1/icc5.0.1-010525z.tar.gz" \
    && echo "2661672232e8845004f40d8aaba15f19cde36750b72b3a864aa21f6a0d196564  /tmp/icc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/icc-5.0.1 \
    && tar xzf /tmp/icc.tar.gz -C /opt/icc-5.0.1 \
    && rm /tmp/icc.tar.gz \
    && chmod +x /opt/icc-5.0.1/Bin/*.exe \
    && ls /opt/icc-5.0.1/Bin/icl.exe \
    && chmod +x /usr/local/bin/icl

COPY icl-wrapper.sh /usr/local/bin/icl
RUN chmod +x /usr/local/bin/icl

ENTRYPOINT ["/usr/local/bin/icl"]

USER rebrew
