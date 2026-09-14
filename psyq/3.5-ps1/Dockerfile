# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-3.5

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 3.5 (PlayStation 1, dosemu2)" \
      org.opencontainers.image.description="PSY-Q 3.5 (MIPS R3000, PS1, DOS binaries under dosemu2) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/mkst/esa/releases/download/psyq-binaries/psyq3.5.tar.gz" \
    && echo "0f9dff42081ad3cc3a1e2f740797b99c28657c3cfe6406deb9de4d176bd5387e  /tmp/psyq.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/parser.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq-obj-parser.tar.gz" \
    && echo "353495f13f6756773cd905ba3a0743843232f95719e306fc6ee56cbf7d731a3e  /tmp/parser.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/psyq-3.5 \
    && tar xzf /tmp/psyq.tar.gz --strip-components=1 -C /opt/psyq-3.5 \
    && rm /tmp/psyq.tar.gz \
    && chmod +x /opt/psyq-3.5/*.EXE \
    && tar xzf /tmp/parser.tar.gz -C /opt/psyq-3.5 \
    && rm /tmp/parser.tar.gz \
    && chmod +x /opt/psyq-3.5/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
