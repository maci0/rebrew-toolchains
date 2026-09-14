# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcc-2.3.3-163e

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 2.3.3-163e (GameCube)" \
      org.opencontainers.image.description="MWCC 2.3.3-163e (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20240706.zip" \
    && echo "399889e059cc86804267eb9376c9c2c4e197d7204936421c45e35fb6c01256c5  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mwcc-2.3.3-163e \
    && unzip -q /tmp/compilers.zip 'GC/1.2.5e/*' -d /tmp/x \
    && cp -a /tmp/x/GC/1.2.5e/. /opt/mwcc-2.3.3-163e/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwcc-2.3.3-163e/mwcceppc.exe

COPY mwcceppc-wrapper.sh /usr/local/bin/mwcceppc
RUN chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
