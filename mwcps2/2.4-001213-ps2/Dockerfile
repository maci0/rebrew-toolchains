# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcps2-2.4-001213

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCPS2 2.4-001213 (PS2)" \
      org.opencontainers.image.description="MWCPS2 2.4-001213 (CodeWarrior PS2, PE/x86_32) toolchain image"

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mwcps2.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/mwcps2-2.4-001213.tar.gz" \
    && echo "0ebe09436b4163c3a109b0431517281501d2de1bd5a0b049d33057710a943e3e  /tmp/mwcps2.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/mwcps2-2.4-001213 \
    && tar xzf /tmp/mwcps2.tar.gz -C /opt/mwcps2-2.4-001213 \
    && rm /tmp/mwcps2.tar.gz \
    && ls /opt/mwcps2-2.4-001213/mwccps2.exe

COPY mwccps2-wrapper.sh /usr/local/bin/mwccps2
RUN chmod +x /usr/local/bin/mwccps2

ENTRYPOINT ["/usr/local/bin/mwccps2"]

USER rebrew
