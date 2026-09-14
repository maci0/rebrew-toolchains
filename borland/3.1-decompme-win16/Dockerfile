# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-3.1-decompme

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 3.1 (decomp.me repack)" \
      org.opencontainers.image.description="Borland C++ 3.1 (decomp.me preservation repack, 16-bit DOS, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc/bcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/bcc3.1.tar.gz" \
    && echo "1fad5133fbe034f00e263e114993fbbcea5ff9ee061449b34e78704ed95af6fc  /tmp/bcc/bcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/bcc3.1dm /tmp/bcc \
    && tar xzf /tmp/bcc/bcc.tar.gz -C /opt/bcc3.1dm \
    && rm -rf /tmp/bcc \
    && ls /opt/bcc3.1dm/bin/bcc.exe

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew
