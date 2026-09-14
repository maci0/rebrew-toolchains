# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp5-pp

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 SP5 + Processor Pack (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp5 + VC6 Processor Pack (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp5_vcpp.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp5_vcpp/tar.gz/refs/heads/master" \
    && echo "1bbf177489054698fd5d29bf042692efdb5bec8719f9dc889b9b1c618c645991  /tmp/msvc600_sp5_vcpp.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp5-pp \
    && tar xzf /tmp/msvc600_sp5_vcpp.tar.gz --strip-components=1 -C /opt/msvc6.0-sp5-pp \
    && rm /tmp/msvc600_sp5_vcpp.tar.gz # CL statically imports mspdb60.dll and only searches its own dir; the

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
