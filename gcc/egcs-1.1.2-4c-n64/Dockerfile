# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gcc-egcs-1.1.2-4c

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew EGCS 1.1.2-4c (N64)" \
      org.opencontainers.image.description="EGCS 1.1.2-4c (N64) (N64, native x86_64) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/mips-gcc-egcs.tar.gz \
        "https://github.com/decompals/mips-gcc-egcs-2.91.66/releases/download/0.7/mips-gcc-egcs-2.91.66-linux.tar.gz" \
    && echo "47b8cfccbad18fba40daa3fb01f4d71da7895d9183ab3ab91d6d7b1d27a715ab  /tmp/tools/mips-gcc-egcs.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/binutils-egcs.tar.gz \
        "https://github.com/decompals/mips-binutils-egcs-2.9.5/releases/download/0.6/mips-binutils-egcs-2.9.5-linux.tar.gz" \
    && echo "54eb249ccfbc9956048de5c740ff41d6ab6137cfc3a872739e465349327bbcbf  /tmp/tools/binutils-egcs.tar.gz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/gcc-egcs-1.1.2-4c /tmp/tools \
    && tar xzf /tmp/tools/mips-gcc-egcs.tar.gz -C /opt/gcc-egcs-1.1.2-4c \
    && tar xzf /tmp/tools/binutils-egcs.tar.gz -C /opt/gcc-egcs-1.1.2-4c \
    && rm -rf /tmp/tools \
    && chmod +x /usr/local/bin/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
