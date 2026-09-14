# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msc-6.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Microsoft C 6.0 (DOS)" \
      org.opencontainers.image.description="Microsoft C 6.0 (16-bit DOS compiler, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msc/msc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/msc600.tar.gz" \
    && echo "d918ee76b25f1e7c55fdcde6de37d4f47ad72e3e69c93e2323802fa951bd60c4  /tmp/msc/msc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msc60 /tmp/msc \
    && tar xzf /tmp/msc/msc.tar.gz -C /opt/msc60 \
    && rm -rf /tmp/msc \
    && ls /opt/msc60/BIN/CL.EXE \
    && chmod +x /usr/local/bin/msc60

COPY msc60-wrapper.sh /usr/local/bin/msc60
RUN chmod +x /usr/local/bin/msc60

ENTRYPOINT ["/usr/local/bin/msc60"]

USER rebrew
