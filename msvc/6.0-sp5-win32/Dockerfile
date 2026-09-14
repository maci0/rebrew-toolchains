# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp5 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp5 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp5.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp5/tar.gz/refs/heads/master" \
    && echo "a95a9c17cbcbe0d97a3e80ef9596f12404eb28f36bab24e89aabcbe37acbbef6  /tmp/msvc600_sp5.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp5 \
    && tar xzf /tmp/msvc600_sp5.tar.gz --strip-components=1 -C /opt/msvc6.0-sp5 \
    && rm /tmp/msvc600_sp5.tar.gz \
    && cp /opt/msvc6.0-sp5/Common/MSDev98/Bin/MSPDB60.DLL /opt/msvc6.0-sp5/VC98/Bin/ \
    && ls /opt/msvc6.0-sp5/VC98/Bin/CL.EXE /opt/msvc6.0-sp5/VC98/Bin/MSPDB60.DLL

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
