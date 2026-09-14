# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ido-5.3

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IDO 5.3 (MIPS, N64)" \
      org.opencontainers.image.description="IDO 5.3 reimplementation (MIPS-II big-endian, N64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ido53.tar.gz \
        "https://github.com/decompals/ido-static-recomp/releases/download/v1.2/ido-5.3-recomp-linux.tar.gz" \
    && echo "ab5c741561f80913d58c8b074771f23941a3edd312505a8ebed6d1dfeb65e506  /tmp/ido53.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ido/5.3 \
    && tar xzf /tmp/ido53.tar.gz -C /opt/ido/5.3 \
    && rm /tmp/ido53.tar.gz \
    && chmod +x /opt/ido/5.3/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
