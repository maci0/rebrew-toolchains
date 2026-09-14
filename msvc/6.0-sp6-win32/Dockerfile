# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp6

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp6 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp6 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp6.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp6/tar.gz/refs/heads/master" \
    && echo "7c2aa3dd4c56b8054cc1ae0e00cd976005dd5b9b43ea8c33b22798a15c9c15c3  /tmp/msvc600_sp6.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp6 \
    && tar xzf /tmp/msvc600_sp6.tar.gz --strip-components=1 -C /opt/msvc6.0-sp6 \
    && rm /tmp/msvc600_sp6.tar.gz # The repo stashes the PDB server DLL in the IDE dir (Common/MSDev98/Bin);

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
