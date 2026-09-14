# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-8.0-portable

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 8.0 portable repack (win32)" \
      org.opencontainers.image.description="MSVC 8.0 (portable preservation repack, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc8p/msvc.zip \
        "https://github.com/widberg/msvc8.0/archive/52c8293f8b8d6441c594cf096542290c17a4d70e.zip" \
    && echo "b138c1b3c99a8a2b9c4324add058e0ddfda5def81f0ef821b10cbfcf383b2084  /tmp/msvc8p/msvc.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/msvc8.0-portable /tmp/msvc8p \
    && unzip -q /tmp/msvc8p/msvc.zip -d /tmp/msvc8p/x \
    && cp -a /tmp/msvc8p/x/msvc8.0-52c8293f8b8d6441c594cf096542290c17a4d70e/. /opt/msvc8.0-portable/ \
    && rm -rf /tmp/msvc8p \
    && ls /opt/msvc8.0-portable/bin/cl.exe

COPY cc-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
