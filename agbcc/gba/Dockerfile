# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: agbcc

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbcc (GBA)" \
      org.opencontainers.image.description="agbcc (pret, GBA, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbcc.tar.gz \
        "https://github.com/pret/agbcc/releases/download/release/agbcc.tar.gz" \
    && echo "bcf0197e3e27d8e08506a142e25fa68ea7f6679a98347a6406804eb3f9ff4d29  /tmp/agbcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/agbcc \
    && tar xzf /tmp/agbcc.tar.gz -C /opt/agbcc \
    && rm /tmp/agbcc.tar.gz \
    && chmod +x /opt/agbcc/bin/agbcc \
    && ls /opt/agbcc/bin/agbcc

COPY agbcc-wrapper.sh /usr/local/bin/agbcc
RUN chmod +x /usr/local/bin/agbcc

ENTRYPOINT ["/usr/local/bin/agbcc"]

USER rebrew
