# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-2.6.3-221

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 2.6.3 (PlayStation 1, dosemu2)" \
      org.opencontainers.image.description="PSY-Q 2.6.3 (MIPS R3000, PS1, DOS binaries under dosemu2) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq_263_221.tar.gz" \
    && echo "082a57e28efe06dc75f1c8be4f2b73ffa65ad5b995c6c345cf67b8dcd19192c5  /tmp/psyq.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/psyq-2.6.3 \
    && tar xzf /tmp/psyq.tar.gz -C /opt/psyq-2.6.3 \
    && rm /tmp/psyq.tar.gz \
    && chmod +x /opt/psyq-2.6.3/*.EXE \
    && chmod +x /usr/local/bin/cc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
