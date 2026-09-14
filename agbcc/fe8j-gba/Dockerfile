# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: agbcc-fe8j

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbcc FE8J (GBA)" \
      org.opencontainers.image.description="agbcc (laqieer FE8J fork, GBA, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbcc.tar.gz \
        "https://github.com/laqieer/agbcc/releases/download/fe8j-v1/agbcc.tar.gz" \
    && echo "5bdeac906031476a341f09929d303c5834d8adda8dc00bd85934eb4b2463daa7  /tmp/agbcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/agbcc-fe8j \
    && tar xzf /tmp/agbcc.tar.gz -C /opt/agbcc-fe8j \
    && rm /tmp/agbcc.tar.gz \
    && chmod +x /opt/agbcc-fe8j/bin/agbcc \
    && ls /opt/agbcc-fe8j/bin/agbcc

COPY agbcc-wrapper.sh /usr/local/bin/agbcc
RUN chmod +x /usr/local/bin/agbcc

ENTRYPOINT ["/usr/local/bin/agbcc"]

USER rebrew
