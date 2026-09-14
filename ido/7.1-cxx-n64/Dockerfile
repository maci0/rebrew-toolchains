# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-7.1-cxx

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 7.1 C++ (MIPS, N64)" \
      org.opencontainers.image.description="IDO 7.1 C++ reimplementation (MIPS-II big-endian, N64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido71.tar.gz \
        "https://github.com/decompals/ido-static-recomp/releases/download/v1.2/ido-7.1-recomp-linux.tar.gz" \
    && echo "0d411696e178fcca34c31c3bf02011b928d7fd9c1fa7f8bf45070e0781b58e15  /tmp/ido71.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ido/7.1 \
    && tar xzf /tmp/ido71.tar.gz -C /opt/ido/7.1 \
    && rm /tmp/ido71.tar.gz \
    && chmod +x /opt/ido/7.1/NCC \
    && ls /opt/ido/7.1/acpp

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
