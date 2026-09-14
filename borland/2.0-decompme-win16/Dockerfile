# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-2.0-decompme

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 2.0 (decomp.me repack)" \
      org.opencontainers.image.description="Borland C++ 2.0 (decomp.me preservation repack, 16-bit DOS, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc/bcc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/bcc2.0.tar.gz" \
    && echo "6a8bb50e1d390e05ea8ef5ea076035eadda32eb1640b5b802538f2c3933565c3  /tmp/bcc/bcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/bcc2.0dm /tmp/bcc \
    && tar xzf /tmp/bcc/bcc.tar.gz -C /opt/bcc2.0dm \
    && rm -rf /tmp/bcc \
    && ls /opt/bcc2.0dm/bin/bcc.exe \
    && chmod +x /usr/local/bin/bcc

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew
