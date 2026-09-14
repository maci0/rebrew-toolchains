# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-egcs-1.1.2-4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EGCS 1.1.2-4 (N64)" \
      org.opencontainers.image.description="EGCS 1.1.2-4 (N64) (N64, native x86_64) toolchain image"

RUN mkdir -p /opt/gcc-egcs-1.1.2-4 /tmp/tools && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/egcs.tar.gz \
        "https://github.com/AngheloAlf/egcs_1.1.2-4/releases/download/latest/egcs_1.1.2-4.tar.gz" \
    && echo "c8d0adeecbe655db1631df5dea58781f4aa738f9762b907f58a6e70740d1815a  /tmp/tools/egcs.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && tar xzf /tmp/tools/egcs.tar.gz -C /opt/gcc-egcs-1.1.2-4 \
    && rm -rf /tmp/tools

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
