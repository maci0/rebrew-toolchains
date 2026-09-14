# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: agbccpp

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew agbccpp (GBA)" \
      org.opencontainers.image.description="agbccpp (notyourav cp fork, GBA, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/agbccpp.tar.gz \
        "https://github.com/notyourav/agbcc/releases/download/cp/agbcc.tar.gz" \
    && echo "05a30f03ee916563bba29efdc9da64c47909892aa878002cf07e8e7ae5bd32f5  /tmp/agbccpp.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/agbccpp \
    && tar xzf /tmp/agbccpp.tar.gz -C /opt/agbccpp \
    && rm /tmp/agbccpp.tar.gz \
    && chmod +x /opt/agbccpp/bin/agbcp \
    && ls /opt/agbccpp/bin/agbcp

COPY agbccpp-wrapper.sh /usr/local/bin/agbccpp
RUN chmod +x /usr/local/bin/agbccpp

ENTRYPOINT ["/usr/local/bin/agbccpp"]

USER rebrew
